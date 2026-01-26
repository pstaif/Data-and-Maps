import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 1. Load Census Tracts (Same as 3d_census.ipynb)
print("Loading Census Tracts...")
url_tracts = "https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_17_tract_500k.zip"
gdf_tracts = gpd.read_file(url_tracts)
gdf_tracts = gdf_tracts[gdf_tracts['COUNTYFP'] == '031'].copy() # Cook County
gdf_tracts = gdf_tracts.to_crs(epsg=4326) # Ensure WGS84

print(f"Loaded {len(gdf_tracts)} tracts.")

# 2. Fetch Crime Data (Chicago Data Portal)
# Endpoint: ijzp-q8t2
# Filter: Year > 2023 (Recent data), limit 10000 for testing
print("Fetching Chicago Crime Data...")
CRIME_API_URL = "https://data.cityofchicago.org/resource/ijzp-q8t2.json?$where=year>2023&$limit=10000"

df_crimes = pd.read_json(CRIME_API_URL)
print(f"Fetched {len(df_crimes)} crimes.")

# 3. Create GeoDataFrame from Crimes
# Drop rows with missing coordinates
df_crimes = df_crimes.dropna(subset=['latitude', 'longitude'])
geometry = [Point(xy) for xy in zip(df_crimes['longitude'], df_crimes['latitude'])]
gdf_crimes = gpd.GeoDataFrame(df_crimes, geometry=geometry, crs="EPSG:4326")

print(f"Valid crime points: {len(gdf_crimes)}")

# 4. Spatial Join (Count Crimes per Tract)
print("Performing Spatial Join...")
# 'inner' join keeps only crimes that fall within a tract
joined = gpd.sjoin(gdf_crimes, gdf_tracts, how="inner", predicate="within")

# Group by Tract info
crime_counts = joined.groupby('GEOID').size().reset_index(name='Crime_Count')
print("Aggregated Crime Counts:")
print(crime_counts.head())

# 5. Merge back to Tracts
gdf_final = gdf_tracts.merge(crime_counts, left_on='GEOID', right_on='GEOID', how='left')
gdf_final['Crime_Count'] = gdf_final['Crime_Count'].fillna(0)

print(f"Final Tracts with Crime Data: {len(gdf_final)}")
print(gdf_final[['GEOID', 'Crime_Count']].describe())
