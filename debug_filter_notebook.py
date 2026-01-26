import json

NOTEBOOK_PATH = '/Users/pstaif/Downloads/MyApps/Data and Maps/kepler_maps.ipynb'

print(f"Reading {NOTEBOOK_PATH}...")
with open(NOTEBOOK_PATH, 'r') as f:
    nb = json.load(f)

# Insert filtering logic BEFORE the point generation loop
filter_code = [
    "# DEBUG: Filter to just one state (TX) to verify code logic and avoid compute timeouts",
    "print('Debugging: Filtering dataset to Texas (TX) only.')",
    "gdf_states = gdf_states[gdf_states['STUSPS'] == 'TX'].copy()",
    "print(f'Filtered GDF size: {len(gdf_states)}')"
]

# We need to find where gdf_states is created/loaded and insert this right after.
# In the original update, we inserted point generation after the geometry cell.
# The geometry cell (Cell 4) ends with `print("Geometry loaded and merged successfully.")`

target_cell_idx = -1
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if "Geometry loaded and merged successfully" in source:
            target_cell_idx = i
            break

if target_cell_idx != -1:
    print(f"Found Geometry cell at {target_cell_idx}. Inserting filter cell after it.")
    
    new_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [l + "\n" for l in filter_code]
    }
    
    nb['cells'].insert(target_cell_idx + 1, new_cell)
    
    with open(NOTEBOOK_PATH, 'w') as f:
        json.dump(nb, f, indent=1)
    print("Added debug filter to notebook.")
else:
    print("Could not find suitable location to insert filter.")
