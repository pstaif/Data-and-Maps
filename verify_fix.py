
import pydeck as pdk
import pandas as pd
import numpy as np
import json

def verify_fix():
    print("Testing DataFrame with numpy types...")
    data = [
        {"lng": -95.7129, "lat": 37.0902, "state": "TX"},
        {"lng": -96.0, "lat": 38.0, "state": "TX"}
    ]
    df = pd.DataFrame(data)
    df['lng'] = df['lng'].astype(float) # float64
    
    # Check what to_dict returns
    records = df.to_dict(orient='records')
    print(f"Type of lng in records: {type(records[0]['lng'])}")
    
    # Try serializing records directly
    try:
        json.dumps(records)
        print("json.dumps(records) worked directly? Yes.")
    except TypeError:
        print("json.dumps(records) failed directly.")

    # With PyDeck
    # Fix strategy: Pass records instead of df
    layer = pdk.Layer(
        "HexagonLayer",
        records, # Passing list of dicts
        get_position=["lng", "lat"],
        radius=100000,
        elevation_scale=50,
        elevation_range=[0, 3000],
        extruded=True,
    )
    
    deck = pdk.Deck(layers=[layer])
    
    try:
        deck.to_json()
        print("Deck with records: Serialization successful!")
    except Exception as e:
        print(f"Deck with records: Serialization failed: {e}")

    # Further robust fix: Explicit conversion
    print("\nTesting robust conversion...")
    clean_records = []
    for r in records:
        clean_records.append({
            "lng": float(r["lng"]),
            "lat": float(r["lat"]),
            "state": str(r["state"])
        })
    
    layer2 = pdk.Layer("HexagonLayer", clean_records, get_position=["lng", "lat"])
    deck2 = pdk.Deck(layers=[layer2])
    try:
        deck2.to_json()
        print("Deck with clean_records: Serialization successful!")
    except Exception as e:
        print(f"Deck with clean_records: Serialization failed: {e}")

if __name__ == "__main__":
    verify_fix()
