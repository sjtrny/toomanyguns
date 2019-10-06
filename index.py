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
    # zoom_y = -1.446 * np.log(width_y) + 7.2753
    # zoom_x = -1.415 * np.log(width_x) + 8.7068
    zoom_y = -1.446 * np.log(width_y) + 8
    zoom_x = -1.415 * np.log(width_x) + 9

    return min(zoom_y, zoom_x)


class Index(BootstrapApp):
    title = "Too Many Guns"
    breadcrumbs = None

    def __init__(self, name, server, url_base_pathname):

        self.token = "pk.eyJ1Ijoic2p0cm55IiwiYSI6ImNrMWJrOGlueTA1ZzMzbHBjeGdtOTN4MHUifQ.V20gMVX6fBu3kyWZaMpI_g"

        file = open("data_generated/nsw.json")
        json_str = file.read()
        file.close()

        self.post_areas_json = json.loads(json_str)
        print(size(getsizeof(json_str)))

        self.post_areas = gpd.read_file(json_str)
        self.post_areas = self.post_areas.set_index("id", drop=False)
        self.post_areas = self.post_areas.dropna()

        hover_text = [
            f"Postcode: {index}<br>"
            f"Firearms: {int(row['Registered Firearms'])}"
            for index, row in self.post_areas.iterrows()
        ]

        fig_data = {
            "type": "choroplethmapbox",
            "geojson": self.post_areas_json,
            "locations": self.post_areas["id"],
            "z": self.post_areas["Registered Firearms"],
            "text": hover_text,
            "hoverinfo": "text",
            "colorscale": "Viridis",
            "marker_opacity": 0.5,
            "marker_line_width": 0,
            "colorbar": {"title": 'Firearms'}
        }

        layout = {
            "mapbox": {
                # center nsw
                "zoom": calc_zoom(-40, -30, 140, 150),
                "center": {"lat": -33, "lon": 146.9211},
                "style": "light",
                "accesstoken": self.token,
            },

            "margin": {"r": 0, "t": 0, "l": 0, "b": 0},
        }

        self.fig = go.Figure(dict(data=[fig_data], layout=layout))

        super().__init__(name, server, url_base_pathname)

    def body(self):

        return [
            mydcc.Relayout(id="mapbox-relayout", aim='mapbox'),
            dbc.Row(
                dbc.Col(html.H1("NSW Firearms Count"), lg=12, style={'text-align': "center"})
            ),
            # dbc.Row(
            #     dbc.Col(html.P(
            #         "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."),
            #             lg=12, style={'text-align': "center"})
            # ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.FormGroup(
                                [
                                    dbc.Label("Postcode", className="h3", style={'margin-bottom': "0px"}),
                                    dbc.FormText(
                                        "Select a postcode to see the stats",
                                        color="secondary",
                                        style={'margin-top': "0px", 'margin-bottom': "8px"}
                                    ),
                                    dcc.Dropdown(
                                        id="postcode",
                                        options=[{"label": code,
                                                  "value": code} for code in
                                                 self.post_areas['id']],
                                        value=None,
                                        placeholder="Select a postcode",
                                        className="h5 text-monospace"
                                    ),

                                ]
                            ),
                        ],
                        lg=4,
                        style={'text-align': "center"}
                    )
                ],
                justify="center"
            ),
            html.Div(id="postcode-stats"),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            id="mapbox",
                            figure=self.fig,
                            config={"displayModeBar": False},
                            style={"height": "600px"}
                        ),
                        lg=12
                    ),
                ],
                style={'margin-top': "20px"}
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
                env = self.post_areas.loc[postcode_selected].geometry.envelope

                zoom_level = calc_zoom(env.bounds[1], env.bounds[3], env.bounds[2], env.bounds[0])

                point = self.post_areas.loc[postcode_selected].geometry.centroid

                lat = point.y
                lon = point.x

                local_layout = {

                    "mapbox": {
                        "zoom": zoom_level,
                        "center": {"lat": lat, "lon": lon},
                        "style": "light",
                        "accesstoken": self.token,
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

            if postcode_selected and self.post_areas.loc[postcode_selected]['parse sucess']:

                card_dict = {
                    "Registered Firearms": self.post_areas.loc[postcode_selected]["Registered Firearms"],
                    "Registered Owners": self.post_areas.loc[postcode_selected]["Registered Firearms Owners"],
                    "Largest Stockpile": self.post_areas.loc[postcode_selected]["Largest stockpile"]

                }

                # row_data = []
                #
                # for k, v in card_dict.items():
                #     row_data.append(
                #         dbc.Col(
                #             html.H4(f"{k}"),
                #             lg=3,
                #             style={'text-align': "center", 'padding': "0px"}
                #         )
                #     )
                #     row_data.append(
                #         dbc.Col(
                #             html.H3(f"{int(v)}", style={'padding': "0px"}),
                #             lg=1,
                #             style={'text-align': "center", 'padding': "0px"}
                #         )
                #     )
                #
                # return row_data


                return [
                    html.Hr(style={"margin-top": "0px"}),
                    dbc.Row(
                        [
                            dbc.Col(
                                # dbc.Card(
                                #     dbc.CardBody(
                                [
                                    html.H4(f"{k}", style={'display': "inline", 'padding-right': "16px"},
                                            className="align-middle"),
                                    html.H2(f"{int(v)}", style={'display': "inline"}, className="align-middle")
                                ],
                                # )
                                # ),
                                lg=4,
                                style={'text-align': "center", 'padding': "0px"},
                            )
                            for k, v in card_dict.items()
                        ],
                        align="center",
                        justify="center"
                    ),
                    html.Hr(),
                ]

            elif postcode_selected:
                return html.P(f"No data for postcode {postcode_selected}")
            else:
                return []
