import json
import os

NOTEBOOK_PATH = "kepler_maps.ipynb"

def update_sf_viz():
    if not os.path.exists(NOTEBOOK_PATH):
        print(f"Error: {NOTEBOOK_PATH} not found.")
        return

    with open(NOTEBOOK_PATH, 'r') as f:
        nb = json.load(f)

    # New Code Cell Content
    new_source = [
        "# Load SF Building Footprints directly from SF Open Data\n",
        "import requests\n",
        "import pandas as pd\n",
        "import geopandas as gpd\n",
        "from shapely.geometry import shape\n",
        "\n",
        "# SODA API Endpoint (Limit to 5000 buildings for performance)\n",
        "DATA_URL = \"https://data.sfgov.org/resource/ynuv-fyni.json?$limit=3000\"\n",
        "\n",
        "try:\n",
        "    print(\"Fetching SF Building Footprints from DataSF...\")\n",
        "    df_sf = pd.read_json(DATA_URL)\n",
        "    \n",
        "    # Convert JSON geometry to Shapely geometry\n",
        "    # The 'shape' column contains GeoJSON-like dicts\n",
        "    if 'shape' in df_sf.columns:\n",
        "        df_sf['geometry'] = df_sf['shape'].apply(lambda x: shape(x) if isinstance(x, dict) else None)\n",
        "        gdf_sf = gpd.GeoDataFrame(df_sf, geometry='geometry')\n",
        "        gdf_sf.crs = \"EPSG:4326\" # SODA API is usually 4326\n",
        "        \n",
        "        # Handle missing heights\n",
        "        gdf_sf['hgt_median_m'] = gdf_sf['hgt_median_m'].fillna(10) # Default to 10m\n",
        "        \n",
        "        print(f\"Loaded {len(gdf_sf)} buildings.\")\n",
        "\n",
        "        # Define Layer\n",
        "        layer_sf = pdk.Layer(\n",
        "            \"GeoJsonLayer\",\n",
        "            gdf_sf,\n",
        "            opacity=0.8,\n",
        "            stroked=False,\n",
        "            filled=True,\n",
        "            extruded=True,\n",
        "            wireframe=False,\n",
        "            get_elevation=\"hgt_median_m\",\n",
        "            get_fill_color=[255, 100, 100],\n",
        "            get_line_color=[255, 255, 255],\n",
        "            pickable=True,\n",
        "            auto_highlight=True,\n",
        "        )\n",
        "\n",
        "        # View State (San Francisco)\n",
        "        view_state_sf = pdk.ViewState(\n",
        "            latitude=37.7749,\n",
        "            longitude=-122.4194,\n",
        "            zoom=13,\n",
        "            pitch=60,\n",
        "            bearing=30\n",
        "        )\n",
        "\n",
        "        deck_sf = pdk.Deck(\n",
        "            layers=[layer_sf],\n",
        "            initial_view_state=view_state_sf,\n",
        "            tooltip={\"text\": \"Height: {hgt_median_m}m\"},\n",
        "            map_style=\"dark\"\n",
        "        )\n",
        "\n",
        "        deck_sf.to_html(\"sf_buildings_real.html\")\n",
        "        deck_sf.show()\n",
        "        print(\"SF Buildings Map generated successfully.\")\n",
        "    else:\n",
        "        print(\"Error: 'shape' column not found in dataset.\")\n",
        "\n",
        "except Exception as e:\n",
        "    print(f\"Error generating SF map: {e}\")\n"
    ]

    # Find and update the cell
    updated = False
    for i, cell in enumerate(nb['cells']):
        source_text = "".join(cell['source'])
        # Look for the cell we added previously
        if "examples/trips/buildings.json" in source_text or "df_buildings = pd.read_json" in source_text:
            cell['source'] = new_source
            updated = True
            print("Updated existing cell with new code.")
            break
            
    if not updated:
        print("Could not find the previous cell to update. Appending new one.")
        # If not found, append
        nb['cells'].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": new_source
        })

    with open(NOTEBOOK_PATH, 'w') as f:
        json.dump(nb, f, indent=1)
    
    print(f"Successfully updated {NOTEBOOK_PATH}")

if __name__ == "__main__":
    update_sf_viz()
