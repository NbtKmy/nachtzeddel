# This code plot locations in a map
import pandas as pd
import geopandas as gpd
from shapely.wkt import loads as load_wkt
import folium

# Load the dataset
df = pd.read_csv('Subset_Origin_With_WTK.csv')

# Drop rows where WTK is missing (optional if you know your dataset is clean)
df_cleaned = df.dropna(subset=['WTK'])

# Convert the WTK column to geometric points using WKT format
df_cleaned['geometry'] = df_cleaned['WTK'].apply(load_wkt)

# Create a GeoDataFrame from the cleaned DataFrame
gdf_cleaned = gpd.GeoDataFrame(df_cleaned, geometry='geometry')

# Filter out invalid or empty geometries
gdf_cleaned = gdf_cleaned[gdf_cleaned['geometry'].apply(lambda geom: geom.is_empty == False and geom.is_valid)]

# Extract latitude and longitude values
gdf_cleaned['latitude'] = gdf_cleaned['geometry'].apply(lambda geom: geom.y)
gdf_cleaned['longitude'] = gdf_cleaned['geometry'].apply(lambda geom: geom.x)

# Calculate map center based on valid coordinates
map_center = [gdf_cleaned['latitude'].mean(), gdf_cleaned['longitude'].mean()]

# Create a folium map centered on the average coordinates
m = folium.Map(location=map_center, zoom_start=6)

# Add points to the map
for _, row in gdf_cleaned.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']], 
        popup=row['Origin']
    ).add_to(m)

# Save the map to an HTML file
m.save('folium_map.html')

print("Map generated and saved as 'folium_map.html'.")
