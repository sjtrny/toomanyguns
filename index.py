import json
from sys import getsizeof
from urllib.parse import urlparse, parse_qsl, urlencode

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import geopandas as gpd
import mydcc
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from hurry.filesize import size

from common import BootstrapApp


def parse_state(url):
    parse_result = urlparse(url)
    params = parse_qsl(parse_result.query)
    state = dict(params)
    return state


def calc_zoom(min_lat, max_lat, min_lng, max_lng):
    width_y = abs(max_lat - min_lat)
    width_x = abs(max_lng - min_lng)
    zoom_y = -1.446 * np.log(width_y) + 7.2753
    zoom_x = -1.415 * np.log(width_x) + 8.7068

    return min(zoom_y, zoom_x)


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


class Index(BootstrapApp):
    title = "Too Many Guns"
    breadcrumbs = None

    def body(self):

        return [
            mydcc.Relayout(id="mapbox-relayout", aim='mapbox'),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            id="mapbox",
                            figure=fig,
                        ),
                        lg=9
                    ),
                    dbc.Col(
                        [
                            dcc.Dropdown(
                                id="postcode",
                                options=[{"label": code,
                                          "value": code} for code in
                                         post_areas['id']],
                                value=None,
                                placeholder="Select a postcode"
                            ),
                            html.Div(id="postcode-stats")
                        ],
                        id="dynamic-layout",
                        lg=3
                    )
                ]
            )
        ]

    def postlayout_setup(self):

        component_ids = [
            'postcode',
        ]

        @self.callback(Output('url', 'search'),
                       inputs=[Input(i, 'value') for i in component_ids])
        def update_url_state(*values):
            state = urlencode(dict(zip(component_ids, values)))
            return f'?{state}'

        @self.callback(
            Output('postcode', 'value'),
            [Input('mapbox', 'clickData'), Input('url', 'href')],
            [State('postcode', 'value')])
        def update_dropdown(click_data, href, current_postcode):

            state = parse_state(href)

            if click_data is None and not state:
                raise PreventUpdate

            clicked_location = click_data['points'][0]['location'] if click_data else None

            source = "mapbox" if current_postcode != clicked_location else "url"

            if source == "mapbox":
                return click_data['points'][0]['location']
            elif source == "url":
                return state['postcode']
            else:
                raise PreventUpdate

        @self.callback(
            Output('mapbox-relayout', 'layout'),
            [Input('postcode', 'value')],
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

        @self.callback(
            Output(component_id="postcode-stats", component_property="children"),
            [Input(component_id="postcode", component_property="value")],
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
