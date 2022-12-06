import streamlit as st
import ee
import folium
from ipyleaflet import LegendControl
import ipyleaflet
import geemap.foliumap as geemap



def app():
    st.title("Heatmap")
    ee.Initialize()

    # ROI
    roi = ee.Geometry.Point([-95.96274061449002, 30.421915524440145])
    location = roi.centroid().coordinates().getInfo()[::-1]

    # Load Landsat 8 data
    bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B7']
    image = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterDate('2020-10-01', '2022-11-20') \
        .filterBounds(roi) \
        .sort('CLOUD_COVER') \
        .first()

    # Import ESRI Data
    lc = ee.ImageCollection("projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m").mosaic().clip(
        image.geometry())
    label = 'b1'

    # Sample the input imagery to get a FeatureCollection of training data.
    sample = image.addBands(lc).sample(**{
        'region': image.geometry(),
        'numPixels': 1000,
        'seed': 0
    })

    # Add a random value field to the sample and use it to approximately split 80%
    # of the features into a training set and 20% into a validation set.
    sample = sample.randomColumn()
    trainingSample = sample.filter('random <= 0.8')
    validationSample = sample.filter('random > 0.8')

    # Train a 10-tree random forest classifier from the training sample.
    trainedClassifier = ee.Classifier.smileRandomForest(10).train(**{
        'features': trainingSample,
        'classProperty': label,
        'inputProperties': bands
    })

    # Classify the reflectance image from the trained classifier.
    model = image.classify(trainedClassifier)



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

    Map = geemap.Map(location=location, zoom_start=8)

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

    # Define a dictionary which will be used to make legend and visualize image on map
    dict = {
        "names": [
            "Water",
            "Trees",
            "Grass",
            "Flooded Vegetation",
            "Crops",
            "Scrub/Shrub",
            "Built Area",
            "Bare Ground",
            "Snow/Ice",
            "Clouds"
        ],

        "colors": [
            "#1A5BAB",
            "#358221",
            "#A7D282",
            "#87D19E",
            "#FFDB5C",
            "#EECFA8",
            "#ED022A",
            "#EDE9E4",
            "#F2FAFF",
            "#C8C8C8"
        ]}
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
    Map.add_ee_layer(lc, {'min': 1, 'max': 10, 'palette': dict['colors']}, 'ESRI LULC 10m')
    Map.add_ee_layer(model, {'min': 1, 'max': 10, 'palette': dict['colors']}, 'Classified 2021')


    visParamsTrue = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000, 'gamma': 1.4}
    Map.add_ee_layer(image, visParamsTrue, "Sentinel 2021")
    Map.add_legend(title='Land Cover Type', labels=labels,colors=colors, draggable=True)
    # Add a layer control panel to the map.
    Map.add_child(folium.LayerControl())

    Map.add_basemap("ROADMAP")
    Map.to_streamlit(height=700)

