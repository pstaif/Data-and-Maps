import json

notebook_path = '/Users/pstaif/Downloads/MyApps/Data and Maps/kepler_maps.ipynb'

try:
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    cells = nb.get('cells', [])
    last_cell = cells[-1] if cells else None
    
    if last_cell and last_cell['cell_type'] == 'code':
        source = "".join(last_cell['source'])
        print("Last Cell Source Snippet:")
        print(source[:200] + "...")
        
        checks = [
            ("NH_FIPS = '33'", "NH FIPS Code"),
            ("radius=5000", "Precise Radius (5000)"),
            ("nh_county_hex_map.html", "Output Filename")
        ]
        
        all_passed = True
        print("\n--- Verification Checks ---")
        for string, description in checks:
            if string in source:
                print(f"[PASS] {description} found.")
            else:
                print(f"[FAIL] {description} NOT found.")
                all_passed = False
                
        if all_passed:
            print("\nSUCCESS: NH County Map cell verified.")
        else:
            print("\nFAILURE: One or more checks failed.")
    else:
        print("FAILURE: Last cell is not a code cell or notebook is empty.")

except Exception as e:
    print(f"Error reading notebook: {e}")
