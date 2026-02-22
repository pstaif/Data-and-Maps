import pandas as pd

# Load the CSV (it's large, so we might want to read line by line or use pandas with iterator)
# But standard pandas read_csv might handle it if enough memory. Let's try iterator.

file_path = '/Users/pstaif/Downloads/MyApps/Data and Maps/variables.csv'

print("Searching variables.csv for 'Employment Status' and 'White'...")

try:
    # Assuming standard format: 'Name', 'Label', 'Concept', etc.
    # Let's inspect the file structure first or just try to find matches in text.
    
    chunksize = 10000
    found_any = False
    
    for df_chunk in pd.read_csv(file_path, chunksize=chunksize, dtype=str):
        # Filter for Race (White) and Employment
        # Labels usually look like "Estimate!!Total!!Male!!16 to 19 years!!In labor force..."
        
        # Look for White Alone
        mask_race = df_chunk['Label'].str.contains('White alone', case=False, na=False) | \
                    df_chunk['Concept'].str.contains('White Alone', case=False, na=False)
        
        if not mask_race.any():
            continue
            
        # Look for Employment
        mask_emp = df_chunk['Label'].str.contains('Employment Status', case=False, na=False) | \
                   df_chunk['Label'].str.contains('In labor force', case=False, na=False) | \
                   df_chunk['Concept'].str.contains('EMPLOYMENT STATUS', case=False, na=False)
                   
        matches = df_chunk[mask_race & mask_emp]
        
        if not matches.empty:
            print("Found matches:")
            print(matches[['Name', 'Label', 'Concept']].head(20))
            found_any = True
            break # Found some, let's analyze first batch
            
    if not found_any:
        print("No matches found for detailed White Employment Status.")

except Exception as e:
    print(f"Error: {e}")
