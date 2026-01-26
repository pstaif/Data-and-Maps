from census import Census
import pandas as pd
import os

# Test Script for 3d_census.ipynb logic
CENSUS_API_KEY = "942e0a44c121ca03ced84b727df9b004f1f1367d"
c = Census(CENSUS_API_KEY)

VARIABLES = {
    "B08301_001E": "Total_Workers",
    "B08301_018E": "Bicycle",
    "B08301_021E": "Work_From_Home"
}

try:
    print("Testing Census API fetch for Cook County...")
    # Cook County is 031, IL is 17
    data = c.acs5.get(("NAME", *VARIABLES.keys()), 
                      {'for': 'tract:*', 'in': 'state:17 county:031', 'year': 2021})
    
    if not data:
        print("Error: No data returned.")
        exit(1)
        
    df = pd.DataFrame(data)
    print(f"Successfully fetched {len(df)} rows.")
    print("Sample:")
    print(df.head())
    
    # Check if variables have non-zero data (to ensure they aren't empty/deprecated)
    df = df.rename(columns=VARIABLES)
    for col in VARIABLES.values():
        df[col] = pd.to_numeric(df[col])
        
    print("\nNon-zero counts:")
    print(df[list(VARIABLES.values())].astype(bool).sum(axis=0))

except Exception as e:
    print(f"API Error: {e}")
    exit(1)
