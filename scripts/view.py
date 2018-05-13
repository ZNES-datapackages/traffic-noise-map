
import folium
from folium import plugins
import json
from geojson import FeatureCollection
from shapely.geometry import mapping, shape
from random import random

with open('data/noisemap.geojson','r') as data_file:
    data = json.load(data_file)

# get centriods from each geojson polygon converted to shapely first
shapes = [
    shape(f['geometry']).centroid for f in data['features']]

# switch lon / lat for folium
hm = [(s.coords[0][1], s.coords[0][0]) for s in shapes]

# basic map
m = folium.Map(
    location=[53, 9],
    tiles=None,
    zoom_start=9)

# add heat map simple! :-)
m.add_children(
    plugins.HeatMap(data=hm, name='Street points', radius=10, ))

# add layers
folium.raster_layers.TileLayer(
    tiles='http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
    attr='google',
    name='google maps',
    max_zoom=20,
    subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
    overlay=False,
    control=True,
).add_to(m)

folium.raster_layers.TileLayer(
    tiles='http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
    attr='google',
    name='google street view',
    max_zoom=20,
    subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
    overlay=False,
    control=True,
).add_to(m)

# for layer control
folium.LayerControl().add_to(m)


m.save('heatmap.html')
