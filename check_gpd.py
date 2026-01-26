import geopandas as gpd
from shapely.geometry import Polygon
import pandas as pd

try:
    print(f"Geopandas version: {gpd.__version__}")
    
    # Create a dummy polygon
    poly = Polygon([(0,0), (10,0), (10,10), (0,10)])
    gs = gpd.GeoSeries([poly])
    
    # Try sample_points (available in gpd >= 0.13)
    if hasattr(gs, 'sample_points'):
        print("Success: sample_points is available.")
        points = gs.sample_points(5)
        print(points)
    else:
        print("Failure: sample_points NOT available.")

except Exception as e:
    print(f"Error checking capabilities: {e}")
