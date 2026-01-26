import json
import os

NOTEBOOK_PATH = "kepler_maps.ipynb"

def add_sf_visualization():
    if not os.path.exists(NOTEBOOK_PATH):
        print(f"Error: {NOTEBOOK_PATH} not found.")
        return

    with open(NOTEBOOK_PATH, 'r') as f:
        nb = json.load(f)

    # Prepare cells
    markdown_cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. San Francisco Building Footprints (3D)\n",
            "Visualizing building heights in San Francisco using 3D extrusion."
        ]
    }

    code_source = [
        "# Load SF Building Footprints Data\n",
        "# Data source: Standard Deck.gl example dataset\n",
        "DATA_URL = \"https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/trips/buildings.json\"\n",
        "\n",
        "try:\n",
        "    print(\"Fetching SF Building Footprints...\")\n",
        "    df_buildings = pd.read_json(DATA_URL)\n",
        "    print(f\"Loaded {len(df_buildings)} building footprints.\")\n",
        "\n",
        "    # Define Layer\n",
        "    layer_buildings = pdk.Layer(\n",
        "        \"PolygonLayer\",\n",
        "        df_buildings,\n",
        "        get_polygon=\"contour\",\n",
        "        get_elevation=\"height\",\n",
        "        get_fill_color=[255, 100, 100, 140],  # Reddish-orange hue\n",
        "        get_line_color=[255, 255, 255, 50],\n",
        "        elevation_scale=1, \n",
        "        extruded=True,\n",
        "        wireframe=False,\n",
        "        pickable=True,\n",
        "        auto_highlight=True\n",
        "    )\n",
        "\n",
        "    # View State (San Francisco)\n",
        "    view_state_sf = pdk.ViewState(\n",
        "        latitude=37.7749295,\n",
        "        longitude=-122.4194155,\n",
        "        zoom=12,\n",
        "        pitch=45,\n",
        "        bearing=0\n",
        "    )\n",
        "\n",
        "    deck_sf = pdk.Deck(\n",
        "        layers=[layer_buildings],\n",
        "        initial_view_state=view_state_sf,\n",
        "        tooltip={\"text\": \"Height: {height}m\"},\n",
        "        map_style=\"dark\"\n",
        "    )\n",
        "\n",
        "    deck_sf.to_html(\"sf_buildings_map.html\")\n",
        "    deck_sf.show()\n",
        "    print(\"SF Buildings Map generated successfully.\")\n",
        "\n",
        "except Exception as e:\n",
        "    print(f\"Error generating SF map: {e}\")\n"
    ]

    code_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": code_source
    }

    # Append
    nb['cells'].append(markdown_cell)
    nb['cells'].append(code_cell)

    with open(NOTEBOOK_PATH, 'w') as f:
        json.dump(nb, f, indent=1)
    
    print(f"Successfully appended new cells to {NOTEBOOK_PATH}")

if __name__ == "__main__":
    add_sf_visualization()
