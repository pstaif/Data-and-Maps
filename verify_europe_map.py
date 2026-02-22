import pandas as pd
import geopandas as gpd
import pydeck as pdk
import numpy as np
import os

print("Starting verification...")

# 1. Define Data
try:
    data = {
        "Country": [
            "Germany", "France", "United Kingdom", "Spain", "Italy", 
            "Switzerland", "Austria", "Belgium", "Sweden", "Netherlands",
            "Portugal", "Greece", "Ireland", "Denmark", "Norway", 
            "Finland", "Czechia", "Poland", "Romania", "Hungary"
        ],
        "Immigrants_Count": [
            17750084, 12986757, 9985453, 7477749, 6553671,
            2089797, 2327064, 2349032, 1422583, 1216237,
            992536, 1423964, 1216237, 847475, 903348,
            514432, 1025199, 445726, 370980, 250912
        ],
        "Immigrant_Pct": [
            21.1, 18.6, 14.2, 15.9, 11.0,
            23.1, 25.5, 20.0, 11.8, 6.5,
            9.4, 14.2, 23.1, 14.9, 16.5,
            9.2, 9.5, 1.2, 1.9, 2.6
        ]
    }

    df = pd.DataFrame(data)

    df['Total_Pop'] = df['Immigrants_Count'] / (df['Immigrant_Pct'] / 100)
    df['Native_Pop'] = df['Total_Pop'] - df['Immigrants_Count']

    df['Total_Pop_M'] = (df['Total_Pop'] / 1e6).round(2)
    df['Immigrants_M'] = (df['Immigrants_Count'] / 1e6).round(2)
    df['Native_Pop_M'] = (df['Native_Pop'] / 1e6).round(2)
    
    print("Dataframe created successfully.")
except Exception as e:
    print(f"Error creating DataFrame: {e}")
    exit(1)

# 2. Load Geometry
try:
    print("Loading geometry...")
    url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    world = gpd.read_file(url)
    # Remove continent filter if column missing, merge will filter for us
    # world = world[world['CONTINENT'] == 'Europe'] 
    merged = world.merge(df, how='inner', left_on='ADMIN', right_on='Country')
    merged = merged.to_crs(epsg=4326)
    print(f"Merged shapes: {merged.shape}")
    if merged.empty:
        print("Warning: Merged dataframe is empty!")
except Exception as e:
    print(f"Error loading/merging geometry: {e}")
    exit(1)

# 3. Visualization
try:
    print("Creating visualization...")
    
    # Elevation Scale Factor
    ELEVATION_SCALE = 0.05

    initial_view_state = pdk.ViewState(
        latitude=50.0,
        longitude=10.0,
        zoom=3,
        pitch=45,
        bearing=0
    )

    # Layer 1: Total Population (Red Base, but will appear as Top)
    total_layer = pdk.Layer(
        "GeoJsonLayer",
        merged,
        opacity=1.0, 
        stroked=True,
        filled=True,
        extruded=True,
        wireframe=True,
        get_elevation="Total_Pop",
        elevation_scale=ELEVATION_SCALE,
        get_fill_color=[255, 0, 0, 200], # Red
        get_line_color=[255, 255, 255],
        pickable=True,
        auto_highlight=True,
    )

    # Layer 2: Native Population (Blue Front)
    native_layer = pdk.Layer(
        "GeoJsonLayer",
        merged,
        opacity=1.0,
        stroked=True,
        filled=True,
        extruded=True,
        wireframe=True,
        get_elevation="Native_Pop",
        elevation_scale=ELEVATION_SCALE,
        get_fill_color=[0, 0, 255, 200], # Blue
        get_line_color=[255, 255, 255],
        pickable=True,
        auto_highlight=True,
    )

    tooltip = {
        "html": "<b>{Country}</b><br>"
                "Total Pop: {Total_Pop_M} M<br>"
                "<span style='color:red'>Immigrants: {Immigrants_M} M ({Immigrant_Pct}%)</span><br>"
                "<span style='color:blue'>Native: {Native_Pop_M} M</span>",
        "style": {
            "backgroundColor": "black",
            "color": "white"
        }
    }

    r = pdk.Deck(
        layers=[total_layer, native_layer], 
        initial_view_state=initial_view_state,
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/dark-v9"
    )

    r.to_html("europe_migration_map.html")
    print("Map generated successfully: europe_migration_map.html")
except Exception as e:
    print(f"Error generating map: {e}")
    exit(1)
