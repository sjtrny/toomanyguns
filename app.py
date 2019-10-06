import json
from sys import getsizeof

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
from dash.exceptions import PreventUpdate
import mydcc

import plotly.graph_objects as go
from hurry.filesize import size

import geopandas as gpd

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

token = "pk.eyJ1Ijoic2p0cm55IiwiYSI6ImNrMWJrOGlueTA1ZzMzbHBjeGdtOTN4MHUifQ.V20gMVX6fBu3kyWZaMpI_g"

if __name__ == "__main__":
    file = open("nsw_debug.json")
else:
    file = open("nsw_live.json")
json_str = file.read()
file.close()

post_areas_json = json.loads(json_str)
print(size(getsizeof(json_str)))

post_areas = gpd.read_file(json_str)
post_areas = post_areas.set_index("id", drop=False)
post_areas = post_areas.dropna()

hover_text = [
                f"Postcode: {index}<br>"
                f"Firearms: {int(row['Registered Firearms'])}"
                for index, row in post_areas.iterrows()
]

fig_data = {
    "type": "choroplethmapbox",
    "geojson": post_areas_json,
    "locations": post_areas["id"],
    "z": post_areas["Registered Firearms"],
    "text": hover_text,
    "hoverinfo": "text",
    "colorscale": "Viridis",
    "marker_opacity": 0.5,
    "marker_line_width": 0
}


def calc_zoom(min_lat,max_lat,min_lng,max_lng):
    width_y = abs(max_lat - min_lat)
    width_x = abs(max_lng - min_lng)
    zoom_y = -1.446*np.log(width_y) + 7.2753
    zoom_x = -1.415*np.log(width_x) + 8.7068

    return min(zoom_y,zoom_x)

layout = {
    "mapbox": {
        # center nsw
        "zoom": calc_zoom(-40, -30, 140, 150),
        "center": {"lat": -33, "lon": 146.9211},
        "style": "light",
        "accesstoken": token,
    },

    "margin": {"r": 0, "t": 0, "l": 0, "b": 0},
}

fig = go.Figure(dict(data=[fig_data], layout=layout))


app.layout = html.Div(
    [
        mydcc.Relayout(id="mapbox-relayout", aim='mapbox' ),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(
                                id="mapbox",
                                figure=fig,
                            ),
                            lg=7
                        ),
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="postcode-dropdown",
                                    options=[{"label": code,
                                              "value": code} for code in
                                             post_areas['id']],
                                    value=None,
                                    placeholder="Select a postcode"
                                ),
                                html.Div(id="postcode-stats")
                            ],

                            lg=3
                        )
                    ]
                )
            ]
        )

    ]
)


@app.callback(
    Output('mapbox-relayout', 'layout'),
    [Input('postcode-dropdown', 'value')],
)
def relayout_mapbox(postcode_selected):

    if postcode_selected:

        env = post_areas.loc[postcode_selected].geometry.envelope

        zoom_level = calc_zoom(env.bounds[1], env.bounds[3], env.bounds[2], env.bounds[0])

        point = post_areas.loc[postcode_selected].geometry.centroid

        lat = point.y
        lon = point.x

        local_layout = {

            "mapbox": {
                "zoom": zoom_level,
                "center": {"lat": lat, "lon": lon},
                "style": "light",
                "accesstoken": token,
            },

            "margin": {"r": 0, "t": 0, "l": 0, "b": 0},
        }

        return local_layout

    raise PreventUpdate


@app.callback(
    Output(component_id="postcode-stats", component_property="children"),
    [Input(component_id="postcode-dropdown", component_property="value")],
)
def update_stats(postcode_selected):

    if postcode_selected and post_areas.loc[postcode_selected]['parse sucess']:
        firearms = post_areas.loc[postcode_selected]["Registered Firearms"]
        owners = post_areas.loc[postcode_selected]["Registered Firearms Owners"]
        stockpile = post_areas.loc[postcode_selected]["Largest stockpile"]

        return dbc.ListGroup(
            [
                dbc.ListGroupItem(
                    [
                        dbc.ListGroupItemHeading("Registered Firearms"),
                        dbc.ListGroupItemText(html.P(firearms))
                    ]
                ),
                dbc.ListGroupItem(
                    [
                        dbc.ListGroupItemHeading("Registered Owners"),
                        dbc.ListGroupItemText(html.P(owners))
                    ]
                ),
                dbc.ListGroupItem(
                    [
                        dbc.ListGroupItemHeading("Largest Stockpile"),
                        dbc.ListGroupItemText(html.P(stockpile))
                    ]
                ),
            ]
        )
    elif postcode_selected:
        return html.P(f"No data for postcode {postcode_selected}")
    else:
        return []

@app.callback(
    Output('postcode-dropdown', 'value'),
    [Input('mapbox', 'clickData')])
def update_dropdown(selected_data):

    if selected_data is None:
        raise PreventUpdate

    return selected_data['points'][0]['location']

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8050, debug=True)
