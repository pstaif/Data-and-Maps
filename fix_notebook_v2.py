
import json

def fix_notebook_v2():
    notebook_path = "kepler_maps.ipynb"
    
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    modified = False
    
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            # Identify by unique content in that cell
            source_joined = "".join(cell['source'])
            if 'layer_hex_density = pdk.Layer' in source_joined:
                new_source = []
                import_added = False
                
                # Check if import json is there
                if 'import json' not in source_joined:
                     new_source.append("import json\n")
                     import_added = True

                for line in cell['source']:
                    # Replace the previous failed attempt or the original code
                    if 'df_points.to_dict' in line or 'df_points,' in line:
                        # Indent properly
                        new_source.append('    json.loads(df_points.to_json(orient=\'records\')),\n')
                        modified = True
                    else:
                        new_source.append(line)
                
                cell['source'] = new_source
                print("Found and patched the target cell.")
                break 
    
    if modified:
        with open(notebook_path, 'w') as f:
            json.dump(nb, f, indent=1)
        print(f"Successfully modified {notebook_path}")
    else:
        print(f"Target cell not modified in {notebook_path}")

if __name__ == "__main__":
    fix_notebook_v2()
