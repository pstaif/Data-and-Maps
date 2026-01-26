import json
import os

NOTEBOOK_PATH = "3d_census.ipynb"

def add_crime_viz():
    if not os.path.exists(NOTEBOOK_PATH):
        print(f"Error: {NOTEBOOK_PATH} not found.")
        return

    with open(NOTEBOOK_PATH, 'r') as f:
        nb = json.load(f)

    # 1. Markdown Cell
    cell_md = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Chicago Crime Density Map (2024-Present)\n",
            "This map visualizes the density of reported crimes in Chicago. \n",
            "- **Height**: Number of Crimes per Tract\n",
            "- **Color**: Number of Crimes (Yellow to Red Heatmap)"
        ]
    }

    # 2. Code Cell - Fetch & Process
    source_process = [
        "# Fetch Chicago Crime Data (2024-Present)\n",
        "# Source: Chicago Data Portal (SODA API)\n",
        "from shapely.geometry import Point\n",
        "\n",
        "try:\n",
        "    print(\"Fetching recent crime data...\")\n",
        "    # Limit to 50,000 recent records for performance/demo\n",
        "    CRIME_API_URL = \"https://data.cityofchicago.org/resource/ijzp-q8t2.json?$where=year>2023&$limit=50000\"\n",
        "    df_crimes = pd.read_json(CRIME_API_URL)\n",
        "    \n",
        "    print(f\"Fetched {len(df_crimes)} crimes.\")\n",
        "    \n",
        "    # Drop invalid coords\n",
        "    df_crimes = df_crimes.dropna(subset=['latitude', 'longitude'])\n",
        "    \n",
        "    # Create GeoDataFrame\n",
        "    geometry = [Point(xy) for xy in zip(df_crimes['longitude'], df_crimes['latitude'])]\n",
        "    gdf_crimes = gpd.GeoDataFrame(df_crimes, geometry=geometry, crs=\"EPSG:4326\")\n",
        "    \n",
        "    # Spatial Join with Tracts\n",
        "    # We use the 'gdf_tracts' loaded in Step 2 (assuming it's still in memory or reload it)\n",
        "    # Note: Ensure gdf_tracts is available. If running sequentially, it is.\n",
        "    \n",
        "    if 'gdf_tracts' not in locals():\n",
        "        # Fallback reload if cell 2 wasn't run or variable lost\n",
        "        print(\"Reloading tracts for join...\")\n",
        "        url = \"https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_17_tract_500k.zip\"\n",
        "        gdf_tracts = gpd.read_file(url)\n",
        "        gdf_tracts = gdf_tracts[gdf_tracts['COUNTYFP'] == '031'].to_crs(epsg=4326)\n",
        "\n",
        "    print(\"Aggregating crimes per tract...\")\n",
        "    joined = gpd.sjoin(gdf_crimes, gdf_tracts[['geometry', 'GEOID', 'TRACTCE']], how=\"inner\", predicate=\"within\")\n",
        "    crime_counts = joined.groupby('GEOID').size().reset_index(name='Crime_Count')\n",
        "    \n",
        "    # Merge back to full tract geometry so we have all tracts (even 0 crime ones)\n",
        "    gdf_crime_map = gdf_tracts.merge(crime_counts, on='GEOID', how='left')\n",
        "    gdf_crime_map['Crime_Count'] = gdf_crime_map['Crime_Count'].fillna(0)\n",
        "    \n",
        "    print(f\"Max crimes in a single tract: {gdf_crime_map['Crime_Count'].max()}\")\n",
        "\n",
        "except Exception as e:\n",
        "    print(f\"Error processing crime data: {e}\")\n"
    ]

    cell_process = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_process
    }

    # 3. Code Cell - Visualize
    source_viz = [
        "# Visualize Crime Density\n",
        "\n",
        "def get_crime_color(count):\n",
        "    # Simple Heatmap: Yellow (Low) -> Red (High)\n",
        "    # Cap at 95th percentile to avoid outliers skewing the scale\n",
        "    max_val = gdf_crime_map['Crime_Count'].quantile(0.95)\n",
        "    if max_val == 0: max_val = 1\n",
        "    \n",
        "    norm = min(1.0, count / max_val)\n",
        "    \n",
        "    # Yellow: [255, 255, 0] -> Red: [255, 0, 0]\n",
        "    # G drops from 255 to 0\n",
        "    return [255, int(255 * (1-norm)), 0, 200]\n",
        "\n",
        "gdf_crime_map['color'] = gdf_crime_map['Crime_Count'].apply(get_crime_color)\n",
        "\n",
        "layer_crime = pdk.Layer(\n",
        "    \"GeoJsonLayer\",\n",
        "    gdf_crime_map,\n",
        "    pickable=True,\n",
        "    stroked=True,\n",
        "    filled=True,\n",
        "    extruded=True,\n",
        "    wireframe=False,\n",
        "    get_fill_color=\"color\",\n",
        "    get_line_color=[255, 255, 255, 80],\n",
        "    get_elevation=\"Crime_Count\",\n",
        "    elevation_scale=20,  # 1 crime = 20m height (Adjust based on max count)\n",
        "    auto_highlight=True,\n",
        ")\n",
        "\n",
        "deck_crime = pdk.Deck(\n",
        "    layers=[layer_crime],\n",
        "    initial_view_state=view_state, # Use same view as Census map\n",
        "    tooltip={\n",
        "        \"html\": \"<b>Tract:</b> {TRACTCE}<br>\" \n",
        "                \"<b>Crimes (2024+):</b> {Crime_Count}\"\n",
        "    },\n",
        "    map_style=\"dark\"\n",
        ")\n",
        "\n",
        "deck_crime.to_html(\"chicago_crime_3d.html\")\n",
        "deck_crime.show()\n",
        "print(\"Chicago Crime Map generated successfully.\")\n"
    ]

    cell_viz = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_viz
    }

    # Append
    nb['cells'].append(cell_md)
    nb['cells'].append(cell_process)
    nb['cells'].append(cell_viz)

    with open(NOTEBOOK_PATH, 'w') as f:
        json.dump(nb, f, indent=1)
    
    print(f"Successfully appended crime map cells to {NOTEBOOK_PATH}")

if __name__ == "__main__":
    add_crime_viz()
