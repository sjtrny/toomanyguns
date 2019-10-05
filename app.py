import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import plotly.graph_objects as go
import numpy as np
from hurry.filesize import size
from sys import getsizeof

app = dash.Dash()

token = "pk.eyJ1Ijoic2p0cm55IiwiYSI6ImNrMWJrOGlueTA1ZzMzbHBjeGdtOTN4MHUifQ.V20gMVX6fBu3kyWZaMpI_g"

if __name__ == "__main__":
    file = open("nsw_debug.json")
else:
    file = open("nsw_live.json")
json_str = file.read()
file.close()
post_areas = json.loads(json_str)
print(size(getsizeof(json_str)))

ids = [feat['properties']['POA_NAME16'] for feat in post_areas['features']]
z = np.array([feat['properties']['Registered Firearms'] for feat in post_areas['features']], dtype=np.float)

fig_data = {
    "type": "choroplethmapbox",
    "geojson": post_areas,
    "locations": ids,
    "z": z,
    "colorscale": "Viridis",
    "zmin": np.nanmin(z),
    "zmax": np.nanmax(z),
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
    server.run(host="0.0.0.0", port=8050, debug=True)