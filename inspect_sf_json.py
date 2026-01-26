import pandas as pd

DATA_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/trips/buildings.json"

print("Fetching data...")
try:
    df = pd.read_json(DATA_URL)
    print(f"Loaded {len(df)} rows.")
    print("Columns:", df.columns.tolist())
    print("\nFirst row sample:")
    print(df.iloc[0].to_dict())
    
    # Check type of 'contour'
    print("\nType of 'contour' in first row:", type(df.iloc[0]['contour']))
    print("Contour sample:", df.iloc[0]['contour'])

except Exception as e:
    print(f"Error: {e}")
