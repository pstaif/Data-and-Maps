import json
import os

notebook_path = '/Users/pstaif/Downloads/MyApps/Data and Maps/kepler_maps.ipynb'

new_code_source = [
    "# 3D Hexagon Layer Map (Hexbin Map)\n",
    "# This plot aggregates data points (state centroids) into hexagonal areas and extrudes them based on Mean Income.\n",
    "\n",
    "# Calculate centroids for point-based aggregation\n",
    "# Note: ensuring we are working with the projected or geographic CRS as needed. \n",
    "# PyDeck expects lon/lat in EPSG:4326, which gdf_states should already be in from previous cells.\n",
    "gdf_states['lon'] = gdf_states.geometry.centroid.x\n",
    "gdf_states['lat'] = gdf_states.geometry.centroid.y\n",
    "\n",
    "# Define the Hexagon Layer\n",
    "hex_layer = pdk.Layer(\n",
    "    \"HexagonLayer\",\n",
    "    gdf_states,\n",
    "    get_position=['lon', 'lat'],\n",
    "    radius=150000,         # Radius in meters (adjust based on desired granularity)\n",
    "    elevation_scale=100,\n",
    "    elevation_range=[0, 3000],\n",
    "    extruded=True,\n",
    "    pickable=True,\n",
    "    get_elevation_weight=VARIABLE_NAME,  # Uses the variable defined earlier, e.g., \"Median_Income\"\n",
    "    elevation_aggregation=\"MEAN\",        # Aggregates using the mean of the values in the bin\n",
    "    auto_highlight=True,\n",
    ")\n",
    "\n",
    "# View State centered on US\n",
    "view_state = pdk.ViewState(\n",
    "    latitude=37.0902,\n",
    "    longitude=-95.7129,\n",
    "    zoom=3,\n",
    "    pitch=45,\n",
    "    bearing=0\n",
    ")\n",
    "\n",
    "# Render Deck\n",
    "deck_hex = pdk.Deck(\n",
    "    layers=[hex_layer],\n",
    "    initial_view_state=view_state,\n",
    "    tooltip={\n",
    "        \"html\": \"<b>Mean Income:</b> {elevationValue}\",\n",
    "        \"style\": {\"color\": \"white\"}\n",
    "    },\n",
    "    map_style=\"dark\",\n",
    ")\n",
    "\n",
    "# Render in Notebook and save HTML\n",
    "deck_hex.to_html(\"census_hex_map.html\")\n",
    "deck_hex.show()"
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
        
    print("Successfully appended new cell to notebook.")

except Exception as e:
    print(f"Error modifying notebook: {e}")
