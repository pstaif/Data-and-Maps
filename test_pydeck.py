
import pydeck as pdk
import pandas as pd
import numpy as np

def test_pydeck_serialization():
    # Create sample data similar to the user's notebook
    data = [
        {"lng": -95.7129, "lat": 37.0902, "state": "TX"},
        {"lng": -96.0, "lat": 38.0, "state": "TX"}
    ]
    df = pd.DataFrame(data)
    
    # Simulate the types in the notebook
    df['lng'] = df['lng'].astype(float)
    df['lat'] = df['lat'].astype(float)
    df['state'] = df['state'].astype(str)
    
    # Define Hexagon Layer
    layer = pdk.Layer(
        "HexagonLayer",
        df,
        get_position=["lng", "lat"],
        radius=100000,
        elevation_scale=50,
        elevation_range=[0, 3000],
        extruded=True,
        pickable=True,
        auto_highlight=True,
        coverage=0.9,
    )
    
    view_state = pdk.ViewState(
        latitude=37.0902,
        longitude=-95.7129,
        zoom=3,
        pitch=45,
        bearing=0
    )
    
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>Point Count:</b> {elevationValue}",
            "style": {"color": "white"}
        },
        map_style="dark",
    )
    
    print("Attempting to serialize...")
    try:
        json_output = deck.to_json()
        print("Serialization successful!")
    except Exception as e:
        print(f"Serialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pydeck_serialization()
