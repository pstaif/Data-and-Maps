import json

NOTEBOOK_PATH = '/Users/pstaif/Downloads/MyApps/Data and Maps/kepler_maps.ipynb'

print(f"Reading {NOTEBOOK_PATH}...")
with open(NOTEBOOK_PATH, 'r') as f:
    nb = json.load(f)

# Improved Code Block
optimized_code = [
    "# Generate Synthetic Population Points (Optimized)",
    "import numpy as np",
    "from shapely.geometry import Point",
    "",
    "def generate_random_points_in_polygon(polygon, num_points):",
    "    # 1. OPTION A: Fast Geopandas sampling (if available)",
    "    try:",
    "        # Check if sample_points exists on GeoSeries",
    "        gs = gpd.GeoSeries([polygon])",
    "        if hasattr(gs, 'sample_points'):",
    "            sampled = gs.sample_points(num_points)",
    "            # Explode in case of MultiPoint outputs",
    "            coords = sampled.explode(index_parts=False)",
    "            return [Point(p.x, p.y) for p in coords]",
    "    except Exception as e:",
    "        # Fallback if specific version issues occur",
    "        pass",
    "",
    "    # 2. OPTION B: Safer Rejection Sampling",
    "    points = []",
    "    min_x, min_y, max_x, max_y = polygon.bounds",
    "    attempts = 0",
    "    # Max attempts to prevent infinite loops on weird geometries",
    "    max_attempts = num_points * 100 + 1000 ",
    "    ",
    "    while len(points) < num_points and attempts < max_attempts:",
    "        attempts += 1",
    "        rand_x = np.random.uniform(min_x, max_x)",
    "        rand_y = np.random.uniform(min_y, max_y)",
    "        p = Point(rand_x, rand_y)",
    "        if polygon.contains(p):",
    "            points.append(p)",
    "            ",
    "    if len(points) < num_points:",
    "        print(f\"Warning: Could only generate {len(points)}/{num_points} points for a geometry.\")",
    "        ",
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
    "    # Safety Cap",
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
    "        except Exception as e:",
    "            print(f\"Skipping {row['NAME']}: {e}\")",
    "",
    "df_points = pd.DataFrame(points_data)",
    "print(f\"Generated {len(df_points)} points representing US population density.\")"
]

# Locate and Replace
found = False
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        # Identify the previous cell we added by checking function definition
        if 'def generate_random_points_in_polygon' in source and 'Rejection sampling' in source:
            print(f"Found logic in cell {i}. Replacing with optimized version...")
            cell['source'] = [l + "\n" for l in optimized_code]
            found = True
            break

if found:
    with open(NOTEBOOK_PATH, 'w') as f:
        json.dump(nb, f, indent=1)
    print("Optimization applied.")
else:
    print("Could not find the specific cell to replace.")
