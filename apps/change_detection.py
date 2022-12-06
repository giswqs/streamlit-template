import streamlit as st
import ee
import os
import datetime
from datetime import date
import folium
from ipyleaflet import LegendControl
import ipyleaflet
import geemap.foliumap as geemap
from shapely.geometry import Polygon
import geopandas as gpd
import fiona
import warnings
import geemap.colormaps as cm


warnings.filterwarnings("ignore")




@st.cache
def uploaded_file_to_gdf(data):
    import tempfile
    import os
    import uuid

    _, file_extension = os.path.splitext(data.name)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(tempfile.gettempdir(), f"{file_id}{file_extension}")

    with open(file_path, "wb") as file:
        file.write(data.getbuffer())

    if file_path.lower().endswith(".kml"):
        fiona.drvsupport.supported_drivers["KML"] = "rw"
        gdf = gpd.read_file(file_path, driver="KML")
    else:
        gdf = gpd.read_file(file_path)

    return gdf

def app():
    st.title("Change Detection")
    ee.Initialize()

    # ROI
    roi = ee.Geometry.Rectangle(-95.8422473420866, 29.51367121002998, -94.48804221535505, 30.112228060191114)

    # select image collection fpr the first sentinel 2 image
    s2_before = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(
        ee.Geometry.Rectangle(-95.8422473420866, 29.51367121002998, -94.48804221535505, 30.112228060191114)) \
        .filterDate('2019-01-01', '2019-11-01') \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    # reduce to single image
    s2_before_red = s2_before.reduce(ee.Reducer.median())

    # select image collection fpr the second sentinel 2 image
    s2_after = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(
        ee.Geometry.Rectangle(-95.8422473420866, 29.51367121002998, -94.48804221535505, 30.112228060191114)) \
        .filterDate('2022-01-01', '2022-11-01') \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    # reduce to single image
    s2_after_red = s2_after.reduce(ee.Reducer.median())

    # select the lclu model for the first date
    dw_before_coll = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1') \
        .filterDate('2019-01-01', '2019-11-01') \
        .filterBounds(roi)

    # clip the sentinel 2 images to the roi
    s2_before_red_clip = s2_before_red.clip(roi)
    s2_after_red_clip = s2_after_red.clip(roi)

    # visuialization parameters for the lclu model
    dwVisParams = {'palette': ['#419BDF', '#397D49', '#88B053', '#7A87C6',
                               '#E49635', '#DFC35A', '#C4281B', '#A59B8F', '#B39FE1'], 'min': 0, 'max': 8}

    # select the lclu model for second date
    dw_after_coll = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1') \
        .filterDate('2022-01-01', '2022-11-01') \
        .filterBounds(roi)

    # mosaic and clip lclu
    dw_before = dw_before_coll.mosaic().clip(roi)
    dw_after = dw_after_coll.mosaic().clip(roi)

    # select the lclu bands
    class_before = dw_before.select('label')
    class_after = dw_after.select('label')

    # visuialization parameters for sentinel-2 images
    mosaic_clipped_viz2 = {'bands': ['B4_median', 'B3_median', 'B2_median'], 'min': 0, 'max': 3000}



    # Define a method for displaying Earth Engine image tiles to folium map.
    def add_ee_layer(self, ee_image_object, vis_params, name):
        map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
        folium.raster_layers.TileLayer(
            tiles=map_id_dict['tile_fetcher'].url_format,
            attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
            name=name,
            overlay=True,
            control=True
        ).add_to(self)

    # Create the map object.

    Map = geemap.Map(Draw_export=True, location=[29.51367121002998, -95.8422473420866], zoom_start=8)

    # Add base map
    basemaps = {'Google Satellite Hybrid': folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite Hybrid',
        overlay=True,
        control=True
    )}
    basemaps['Google Satellite Hybrid'].add_to(Map)

    folium.Map.add_ee_layer = add_ee_layer
    ipyleaflet.LegendControl = LegendControl


    colors = ["#1A5BAB",
            "#358221",
            "#A7D282",
            "#87D19E",
            "#FFDB5C",
            "#EECFA8",
            "#ED022A",
            "#EDE9E4",
            "#F2FAFF",
            "#C8C8C8"]
    labels = ["Water",
            "Trees",
            "Grass",
            "Flooded Vegetation",
            "Crops",
            "Scrub/Shrub",
            "Built Area",
            "Bare Ground",
            "Snow/Ice",
            "Clouds"]

    # Add land cover to the map object.
    # add map layers
    Map.add_ee_layer(s2_before_red_clip, mosaic_clipped_viz2, 's2_before')
    Map.add_ee_layer(s2_after_red_clip, mosaic_clipped_viz2, 'S2_after')
    Map.add_ee_layer(class_before, dwVisParams, 'LULC_before')
    Map.add_ee_layer(class_after, dwVisParams, 'LULC_after')

    ##BARE
    bare_before = dw_before.select('bare')
    bare_after = dw_after.select('bare')
    new_bare = bare_before.lt(0.25).And(bare_after.gt(0.55))
    new_bare = new_bare.updateMask(new_bare)
    Map.add_ee_layer(new_bare, {min: 0, max: 1, 'palette': ['white', 'beige']}, 'new_bare')

    ##BUILT
    built_before = dw_before.select('built')
    built_after = dw_after.select('built')
    new_built = built_before.lt(0.25).And(built_after.gt(0.6))
    new_built = new_built.updateMask(new_built)
    Map.add_ee_layer(new_built, {min: 0, max: 1, 'palette': ['white', 'red']}, 'new_built')

    # Add a layer control panel to the map.
    Map.add_child(folium.LayerControl())
    Map.add_legend(title='Land Cover Type', labels=labels,colors=colors, draggable=True)


    Map.add_basemap("ROADMAP")
    Map.to_streamlit(height=700)