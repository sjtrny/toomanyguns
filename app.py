import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import geopandas as gpd
import plotly.graph_objects as go
import numpy as np
import io
from hurry.filesize import size
import pandas as pd

app = dash.Dash()

token = "pk.eyJ1Ijoic2p0cm55IiwiYSI6ImNrMWJrOGlueTA1ZzMzbHBjeGdtOTN4MHUifQ.V20gMVX6fBu3kyWZaMpI_g"

firearms = pd.read_csv("2019.csv", index_col=0)
firearms = firearms.set_index('postcode')

geodf = gpd.read_file("shapes/POA_2016_AUST.shp")
geodf['POA_CODE16'] = geodf['POA_CODE16'].astype(int)

nsw = geodf[(geodf['POA_CODE16'] >=2000) & (geodf['POA_CODE16'] < 3000)]

nsw['geometry'] = nsw['geometry'].simplify(tolerance=0.00035)

proxyIO = io.BytesIO()
nsw.to_file(proxyIO, driver='GeoJSON')
print(size(proxyIO.tell()))

post_areas = json.loads(proxyIO.getvalue().decode('utf-8'))

# Add id
for feat in post_areas['features']:
    feat['id'] = feat['properties']['POA_NAME16']
    feat['properties']['count'] = firearms.loc[feat['properties']['POA_CODE16']]['Registered Firearms'] if feat['properties']['POA_CODE16'] in firearms.index else np.NaN

ids = [feat['properties']['POA_NAME16'] for feat in post_areas['features']]
z = [feat['properties']['count'] for feat in post_areas['features']]

fig_data = {
    "type": "choroplethmapbox",
    "geojson": post_areas,
    "locations": ids,
    "z": z,
    "colorscale": "Viridis",
    "zmin": firearms['Registered Firearms'].min(),
    "zmax": firearms['Registered Firearms'].max(),
    "marker_opacity": 0.5,
    "marker_line_width": 0
}

layout = {
    "mapbox_zoom": 12,
    "mapbox_center": {"lat": -33.8688, "lon": 151.20939},
    "mapbox_style": "light",
    "mapbox_accesstoken": token,
    "margin": {"r": 0, "t": 0, "l": 0, "b": 0},
}


fig = go.Figure(dict(data=[fig_data], layout=layout))

app.layout = html.Div([
    dcc.Graph(
        id = "mapbox",
        figure = fig,
        style = {"height": "100vh", "width": "100vw"}
    ),
])

server = app.server

if __name__ == "__main__":
    server.run(host="0.0.0.0", debug=True)