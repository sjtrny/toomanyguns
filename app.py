import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
import geopandas as gpd
import plotly.graph_objects as go
import numpy as np
import io
from hurry.filesize import size
from dash.exceptions import PreventUpdate
from shapely.geometry import Polygon
from collections import OrderedDict

app = dash.Dash()

geodf = gpd.read_file("shapes/POA_2016_AUST.shp")
geodf['POA_CODE16'] = geodf['POA_CODE16'].astype(int)

nsw = geodf[(geodf['POA_CODE16'] >=2000) & (geodf['POA_CODE16'] < 3000)]

token = ....

app.layout = html.Div([
    dcc.Graph(
        id = "mapbox",
        style = {"height": "100vh", "width": "100vw"}
    ),
    html.Pre(id='relayout-data')
])

@app.callback(
    Output('mapbox', 'figure'),
    [Input('mapbox', 'relayoutData')])
def display_relayout_data(relayoutData):

    if relayoutData is None:
        raise PreventUpdate

    if "mapbox.zoom" not in relayoutData:
        layout = {
            "mapbox_zoom": 5.5,
            "mapbox_center": {"lat": -33.8688, "lon": 151.20939},
        }
    else:
        layout = {k.replace(".", "_"): v for k, v in relayoutData.items()}

    center = layout["mapbox_center"]
    zoom = layout["mapbox_zoom"]

    zoom_geo_mapping = {
        0: 35,
        6: 3,
        9: 0.25
    }

    zoom_levels = np.sort(np.array(list(zoom_geo_mapping.keys())))

    zoom_snapped_idx = np.max(np.where(zoom >= zoom_levels))
    offset = zoom_geo_mapping[zoom_levels[zoom_snapped_idx]]

    top = center["lat"] + offset
    bottom = center["lat"] - offset
    left = center["lon"] - offset
    right = center["lon"] + offset

    bounds = Polygon([(left, top), (right, top), (right, bottom), (left, bottom)])

    bounded_df = nsw[nsw.geometry.within(bounds)]

    zoom_tol_mapping = {
        0: 0.5,
        1: 0.1,
        3: 0.025,
        6: 0.0025,
        9: 0.00025,
    }

    zoom_levels = np.sort(np.array(list(zoom_tol_mapping.keys())))

    zoom_snapped_idx = np.max(np.where(zoom >= zoom_levels))
    tol = zoom_tol_mapping[zoom_levels[zoom_snapped_idx]]

    bounded_df['geometry'] = bounded_df['geometry'].simplify(tolerance=tol)

    proxyIO = io.BytesIO()

    schema = gpd.io.file.infer_schema(bounded_df)

    schema["id"] = OrderedDict({"id": "int"})
    bounded_df.to_file(proxyIO, driver='GeoJSON', schema=schema)
    print(size(proxyIO.tell()))

    post_areas = json.loads(proxyIO.getvalue().decode('utf-8'))

    # Add id
    for feat in post_areas['features']:
        feat['id'] = feat['properties']['POA_NAME16']

    ids = [feat['properties']['POA_NAME16'] for feat in post_areas['features']]

    fig_data = {
        "type": "choroplethmapbox",
        "geojson": post_areas,
        "locations": ids,
        "z": np.random.rand(len(ids)),
        "colorscale": "Viridis",
        "zmin": 0,
        "zmax": 1,
        "marker_opacity": 0.5,
        "marker_line_width": 0
    }

    layout["margin"] = {"r": 0, "t": 0, "l": 0, "b": 0}
    layout["mapbox_style"] = "light"
    layout["mapbox_accesstoken"] = token

    fig_layout = layout

    fig = go.Figure(dict(data=[fig_data], layout=fig_layout))

    return fig


# @app.callback(
#     Output('relayout-data', 'children'),
#     [Input('mapbox', 'relayoutData')])
# def display_relayout_data(relayoutData):
#     return json.dumps(relayoutData, indent=2)

server = app.server

app.run_server(host="0.0.0.0")