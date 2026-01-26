import pandas as pd
import requests

# SF Open Data: Building Footprints
# https://data.sfgov.org/Housing-and-Buildings/Building-Footprints/ynuv-fyni
DATA_URL = "https://data.sfgov.org/resource/ynuv-fyni.json?$limit=5"

try:
    print(f"Fetching data from {DATA_URL}...")
    df = pd.read_json(DATA_URL)
    print(f"Loaded {len(df)} rows.")
    print("Columns:", df.columns.tolist())
    
    if not df.empty:
        row = df.iloc[0]
        print("\nSample Row:")
        print(row)
        print("\nGeometry type:", type(row.get('the_geom')))
        print("Geometry content:", row.get('the_geom'))

except Exception as e:
    print(f"Error: {e}")
