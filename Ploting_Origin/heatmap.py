# code to plot a heatmap showing the occurence of origine places along the dataset

import pandas as pd
import geopandas as gpd
from shapely.wkt import loads as load_wkt
import folium
from folium.plugins import HeatMap

# Load the dataset
file_path = 'Subset_Origin_With_WTK.csv'
df = pd.read_csv(file_path)

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

# Group data by Origin and count occurrences
df_grouped = gdf_cleaned.groupby(['Origin', 'latitude', 'longitude']).size().reset_index(name='count')

# Calculate map center based on valid coordinates
map_center = [gdf_cleaned['latitude'].mean(), gdf_cleaned['longitude'].mean()]

# Create a folium map centered on the average coordinates
m = folium.Map(location=map_center, zoom_start=6)

# Prepare data for the heatmap: [[lat, long, intensity], ...]
heat_data = [[row['latitude'], row['longitude'], row['count']] for index, row in df_grouped.iterrows()]

# Create the heatmap layer
HeatMap(heat_data).add_to(m)

# Save the heatmap to an HTML file
output_path = 'heatmap.html'
m.save(output_path)

output_path  # Return the path to the saved HTML file
