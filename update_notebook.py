import json
import random

NOTEBOOK_PATH = '/Users/pstaif/Downloads/MyApps/Data and Maps/kepler_maps.ipynb'

def create_code_cell(source_lines):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source_lines]
    }

def create_markdown_cell(source_lines):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source_lines]
    }

print(f"Reading {NOTEBOOK_PATH}...")
with open(NOTEBOOK_PATH, 'r') as f:
    nb = json.load(f)

# 1. UPDATE FETCH CELL
# Find cell with CENSUS_API_KEY
fetch_cell = None
fetch_cell_idx = -1
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if 'CENSUS_API_KEY =' in source and 'Median_Income' in source:
            fetch_cell = cell
            fetch_cell_idx = i
            break

if fetch_cell:
    print(f"Found Fetch Cell at index {fetch_cell_idx}. Updating source...")
    new_fetch_source = [
        "# REPLACE WITH YOUR API KEY",
        "CENSUS_API_KEY = \"942e0a44c121ca03ced84b727df9b004f1f1367d\"",
        "c = Census(CENSUS_API_KEY)",
        "",
        "# Variables: Median Income (B19013_001E), Population (B01003_001E)",
        "VARIABLES = {",
        "    \"B19013_001E\": \"Median_Income\",",
        "    \"B01003_001E\": \"Population\"",
        "}",
        "",
        "try:",
        "    # Fetch data for all states (Year 2021)",
        "    # We pass the list of variable codes as a tuple",
        "    census_data = c.acs5.get((\"NAME\", *VARIABLES.keys()), {'for': 'state:*', 'year': 2021})",
        "    ",
        "    if not census_data:",
        "        raise ValueError(\"API returned empty data.\")",
        "        ",
        "    # Convert to DataFrame",
        "    df_census = pd.DataFrame(census_data)",
        "    ",
        "    # Rename columns using the mapping",
        "    df_census = df_census.rename(columns=VARIABLES)",
        "    df_census = df_census.rename(columns={\"state\": \"STATEFP\"})",
        "    ",
        "    # Convert numeric columns",
        "    for col in VARIABLES.values():",
        "        df_census[col] = pd.to_numeric(df_census[col])",
        "    ",
        "    print(f\"Successfully fetched data for {len(df_census)} states.\")",
        "    print(df_census.head())",
        "    ",
        "except Exception as e:",
        "    print(f\"Error fetching data: {e}\")"
    ]
    nb['cells'][fetch_cell_idx]['source'] = [l + "\n" for l in new_fetch_source]

# 2. INSERT POINT GENERATION CELL AFTER GEOMETRY LOAD
geo_cell_idx = -1
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if 'gpd.read_file' in source and 'cb_2021_us_state_20m' in source:
            geo_cell_idx = i
            break

if geo_cell_idx != -1:
    print(f"Found Geometry Cell at {geo_cell_idx}. Inserting Point Generation Code...")
    
    point_gen_source = [
        "# Generate Synthetic Population Points",
        "# For a true Hexbin density map, we need points representing people.",
        "import numpy as np",
        "from shapely.geometry import Point",
        "",
        "def generate_random_points_in_polygon(polygon, num_points):",
        "    points = []",
        "    min_x, min_y, max_x, max_y = polygon.bounds",
        "    # Rejection sampling",
        "    while len(points) < num_points:",
        "        rand_x = np.random.uniform(min_x, max_x)",
        "        rand_y = np.random.uniform(min_y, max_y)",
        "        p = Point(rand_x, rand_y)",
        "        if polygon.contains(p):",
        "            points.append(p)",
        "    return points",
        "",
        "points_data = []",
        "SCALE = 100000  # 1 dot = 100k people",
        "",
        "print(f\"Generating synthetic points (Scale: 1 dot = {SCALE:,} people)...\")",
        "",
        "for idx, row in gdf_states.iterrows():",
        "    pop = row.get('Population', 0)",
        "    if pd.isna(pop) or pop <= 0:",
        "        continue",
        "    ",
        "    n_points = int(pop / SCALE)",
        "    # Cap n_points for performance in this demo",
        "    if n_points > 2000: n_points = 2000",
        "    ",
        "    if n_points > 0:",
        "        try:",
        "            pts = generate_random_points_in_polygon(row.geometry, n_points)",
        "            for p in pts:",
        "                points_data.append({",
        "                    \"lng\": p.x,",
        "                    \"lat\": p.y,",
        "                    \"state\": row[\"NAME\"]",
        "                })",
        "        except Exception:",
        "            pass",
        "",
        "df_points = pd.DataFrame(points_data)",
        "print(f\"Generated {len(df_points)} points representing US population density.\")"
    ]
    
    nb['cells'].insert(geo_cell_idx + 1, create_code_cell(point_gen_source))

# 3. APPEND MARKDOWN AND HEXBIN LAYER CELL
print("Appending Hexbin Density Map Cell...")

markdown_source = [
    "## 3. Population Density Hexbin Map",
    "This map aggregates the synthetic population points into hexagons. The height and color of each hexagon represent the density of points (people) in that area."
]
nb['cells'].append(create_markdown_cell(markdown_source))

hex_layer_source = [
    "# Define Hexagon Layer for Population Density",
    "layer_hex_density = pdk.Layer(",
    "    \"HexagonLayer\",",
    "    df_points,",
    "    get_position=[\"lng\", \"lat\"],",
    "    radius=100000,          # 100km radius",
    "    elevation_scale=50,",
    "    elevation_range=[0, 3000],",
    "    extruded=True,",
    "    pickable=True,",
    "    auto_highlight=True,",
    "    coverage=0.9,",
    "    material=True",
    ")",
    "",
    "view_state_us = pdk.ViewState(",
    "    latitude=37.0902,",
    "    longitude=-95.7129,",
    "    zoom=3,",
    "    pitch=45,",
    "    bearing=0",
    ")",
    "",
    "deck_density = pdk.Deck(",
    "    layers=[layer_hex_density],",
    "    initial_view_state=view_state_us,",
    "    tooltip={",
    "        \"html\": \"<b>Point Count:</b> {elevationValue} <br/> (Approx {elevationValue}00k people)\",",
    "        \"style\": {\"color\": \"white\"}",
    "    },",
    "    map_style=\"dark\",",
    ")",
    "",
    "deck_density.to_html(\"census_population_hex_map.html\")",
    "deck_density.show()"
]
nb['cells'].append(create_code_cell(hex_layer_source))

# WRITE
print(f"Writing updates to {NOTEBOOK_PATH}...")
with open(NOTEBOOK_PATH, 'w') as f:
    json.dump(nb, f, indent=1)

print("Done.")
