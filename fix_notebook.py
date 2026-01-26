
import json

def fix_notebook():
    notebook_path = "kepler_maps.ipynb"
    
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    modified = False
    
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            # Look for the specific cell by ID or content
            # ID from previous `view_file` was "4ffffeb9"
            if cell.get('id') == "4ffffeb9":
                new_source = []
                for line in cell['source']:
                    if '    df_points,\n' in line:
                        new_source.append('    df_points.to_dict(orient=\'records\'),\n')
                        modified = True
                    else:
                        new_source.append(line)
                cell['source'] = new_source
                break 
    
    if modified:
        with open(notebook_path, 'w') as f:
            json.dump(nb, f, indent=1) # Formatting might change slightly but that's okay for json
        print(f"Successfully modified {notebook_path}")
    else:
        print(f"Target line not found in {notebook_path}")

if __name__ == "__main__":
    fix_notebook()
