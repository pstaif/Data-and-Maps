
import pydeck as pdk
import pandas as pd
import numpy as np
import json

def debug_types():
    print("Creating DataFrame with explicit numpy types...")
    # Create data with numpy types
    df = pd.DataFrame({
        "lng": [np.float64(-95.7129)], 
        "lat": [np.float64(37.0902)], 
        "val": [np.int64(10)]
    })
    
    # 1. Check to_dict behavior
    records = df.to_dict(orient='records')
    sample = records[0]
    print(f"Sample record keys: {sample.keys()}")
    print(f"Type of 'lng': {type(sample['lng'])}")
    print(f"Type of 'val': {type(sample['val'])}")
    
    # 2. Mimic PyDeck serialization trigger
    # PyDeck's default serializer tries vars() on unknown objects
    from pydeck.bindings.json_tools import default_serialize
    
    print("\nTesting default_serialize on numpy types:")
    try:
        val = sample['lng']
        # This is what json.dumps calls when it sees a numpy float and doesn't know what to do
        default_serialize(val, None) 
        print("Success: default_serialize handled numpy float (unexpected)")
    except TypeError as e:
        print(f"Caught expected TypeError on float: {e}")
        
    try:
        val = sample['val']
        default_serialize(val, None) 
        print("Success: default_serialize handled numpy int (unexpected)")
    except TypeError as e:
        print(f"Caught expected TypeError on int: {e}")

    # 3. Verify Robust Fix
    print("\nTesting Robust Fix: json.loads(df.to_json())...")
    clean_records = json.loads(df.to_json(orient='records'))
    clean_sample = clean_records[0]
    print(f"Clean Type of 'lng': {type(clean_sample['lng'])}")
    
    layer = pdk.Layer("HexagonLayer", clean_records)
    deck = pdk.Deck([layer])
    try:
        deck.to_json()
        print("Deck with clean_records: Serialization successful!")
    except Exception as e:
        print(f"Deck with clean_records: Serialization failed: {e}")

if __name__ == "__main__":
    debug_types()
