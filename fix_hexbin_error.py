import json

NOTEBOOK_PATH = '/Users/pstaif/Downloads/MyApps/Data and Maps/kepler_maps.ipynb'

print(f"Reading {NOTEBOOK_PATH}...")
with open(NOTEBOOK_PATH, 'r') as f:
    nb = json.load(f)

found_and_fixed = False

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        new_source = []
        changed = False
        for line in cell['source']:
            # Check for the problematic line. 
            # It might have a trailing comma or newline
            if 'material=True' in line:
                print(f"Found culprit in cell {i}: {line.strip()}")
                # Skip this line (remove it)
                changed = True
                found_and_fixed = True
            else:
                new_source.append(line)
        
        if changed:
            cell['source'] = new_source
            print(f"Fixed cell {i}")

if found_and_fixed:
    print(f"Writing updates to {NOTEBOOK_PATH}...")
    with open(NOTEBOOK_PATH, 'w') as f:
        json.dump(nb, f, indent=1)
    print("Notebook fixed successfully.")
else:
    print("Could not find 'material=True' in the notebook. No changes made.")
