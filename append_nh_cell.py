import json
import os

notebook_path = '/Users/pstaif/Downloads/MyApps/Data and Maps/kepler_maps.ipynb'

new_code_source = [
    "# New Hampshire County Level 3D Hexagon Map\n",
    "# More precise visualization for NH counties\n",
    "\n",
    "NH_FIPS = '33'\n",
    "\n",
    "try:\n",
    "    # 1. Fetch County Data for NH\n",
    "    print(\"Fetching county data for New Hampshire...\")\n",
    "    nh_census = c.acs5.get((\"NAME\", VARIABLE_CODE), {'for': 'county:*', 'in': f'state:{NH_FIPS}', 'year': 2021})\n",
    "    \n",
    "    if not nh_census:\n",
    "        raise ValueError(\"API returned empty data for NH counties.\")\n",
    "        \n",
    "    df_nh = pd.DataFrame(nh_census)\n",
    "    df_nh = df_nh.rename(columns={VARIABLE_CODE: VARIABLE_NAME, \"state\": \"STATEFP\", \"county\": \"COUNTYFP\"})\n",
    "    df_nh[VARIABLE_NAME] = pd.to_numeric(df_nh[VARIABLE_NAME])\n",
    "    \n",
    "    # 2. Geometry: Load US Counties and Filter for NH\n",
    "    # Note: Using 20m resolution for consistency, but 5m or 500k might be better for zooming.\n",
    "    # Since we used 20m for states, we'll use 20m for counties unless precise borders are needed.\n",
    "    # Given 'more precise' request, let's try to stick to what works first.\n",
    "    county_url = \"https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_county_20m.zip\"\n",
    "    print(\"Loading US County geometry...\")\n",
    "    gdf_counties = gpd.read_file(county_url)\n",
    "    \n",
    "    # Filter for NH\n",
    "    gdf_nh = gdf_counties[gdf_counties['STATEFP'] == NH_FIPS].copy()\n",
    "    \n",
    "    # 3. Merge\n",
    "    gdf_nh = gdf_nh.merge(df_nh, on=[\"STATEFP\", \"COUNTYFP\"], how=\"left\")\n",
    "    gdf_nh = gdf_nh.dropna(subset=[VARIABLE_NAME])\n",
    "    gdf_nh = gdf_nh.to_crs(epsg=4326)\n",
    "    \n",
    "    # 4. Calculate Centroids for Hex Points\n",
    "    gdf_nh['lon'] = gdf_nh.geometry.centroid.x\n",
    "    gdf_nh['lat'] = gdf_nh.geometry.centroid.y\n",
    "    \n",
    "    # 5. Hexagon Layer (Higher Precision)\n",
    "    hex_layer_nh = pdk.Layer(\n",
    "        \"HexagonLayer\",\n",
    "        gdf_nh,\n",
    "        get_position=['lon', 'lat'],\n",
    "        radius=5000,           # 5km radius for finer granularity\n",
    "        elevation_scale=100,\n",
    "        elevation_range=[0, 3000],\n",
    "        extruded=True,\n",
    "        pickable=True,\n",
    "        get_elevation_weight=VARIABLE_NAME,\n",
    "        elevation_aggregation=\"MEAN\",\n",
    "        auto_highlight=True,\n",
    "        coverage=0.9           # Slightly separated hexagons\n",
    "    )\n",
    "    \n",
    "    # View State centered on NH\n",
    "    view_state_nh = pdk.ViewState(\n",
    "        latitude=43.7939,     # Approx NH center\n",
    "        longitude=-71.5724,\n",
    "        zoom=7,\n",
    "        pitch=45,\n",
    "        bearing=0\n",
    "    )\n",
    "    \n",
    "    deck_nh = pdk.Deck(\n",
    "        layers=[hex_layer_nh],\n",
    "        initial_view_state=view_state_nh,\n",
    "        tooltip={\n",
    "            \"html\": \"<b>Mean Income:</b> {elevationValue}\",\n",
    "            \"style\": {\"color\": \"white\"}\n",
    "        },\n",
    "        map_style=\"dark\",\n",
    "    )\n",
    "    \n",
    "    deck_nh.to_html(\"nh_county_hex_map.html\")\n",
    "    deck_nh.show()\n",
    "    print(\"NH County Map generated successfully!\")\n",
    "    \n",
    "except Exception as e:\n",
    "    print(f\"Error generating NH map: {e}\")"
]

new_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": new_code_source
}

try:
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    nb['cells'].append(new_cell)
    
    with open(notebook_path, 'w') as f:
        json.dump(nb, f, indent=1)
        
    print("Successfully appended NH County Map cell to notebook.")

except Exception as e:
    print(f"Error modifying notebook: {e}")
