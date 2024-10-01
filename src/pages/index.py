import json
from urllib.parse import parse_qsl, urlencode, urlparse

import dash
import dash_bootstrap_components as dbc
import geopandas as gpd
from dash import Input, Output, State, callback, dcc, html
import plotly.express as px
import numpy as np

def parse_state(url):
    parse_result = urlparse(url)
    params = parse_qsl(parse_result.query)
    state = dict(params)
    return state


dash.register_page(__name__, path="/", title="Too Many Guns")

file = open("data_generated/nsw.json")
json_str = file.read()
file.close()

post_areas_json = json.loads(json_str)

post_areas = gpd.read_file(json_str)
post_areas = post_areas.set_index("id", drop=False)
post_areas = post_areas.dropna()

# 2898 - Lord Howe Island
# 2899 - Norfolk Pine
post_areas = post_areas.drop(["2898", "2899"])

layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(html.A("About", href="/about", className="nav-link")),
            ],
            brand="Too Many Guns",
            brand_href="/",
            brand_external_link=True,
            color="dark",
            dark=True,
            className="mb-4",
        ),
        dbc.Container(
            [
                dbc.Row(
                    dbc.Col(
                        html.H2("NSW Firearms Count"),
                        lg=12,
                        style={"text-align": "center"},
                    )
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.FormText(
                                            "Select a postcode to see the stats",
                                            color="secondary",
                                            style={
                                                "margin-top": "0px",
                                                "margin-bottom": "0px",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="postcode-selected",
                                            options=[
                                                {"label": code, "value": code}
                                                for code in post_areas["id"]
                                            ],
                                            value=None,
                                            placeholder="Postcode",
                                            className="h5 text-monospace",
                                        ),
                                    ]
                                )
                            ],
                            lg=4,
                            style={"text-align": "center"},
                        )
                    ],
                    justify="center",
                ),
                html.Div(id="postcode-stats"),
                dcc.Loading(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Graph(
                                            id="map",
                                            config={
                                                "displayModeBar": False,
                                                "responsive": True,
                                            },
                                            style={
                                                "height": "75vh",
                                                "margin-bottom": "32px",
                                            },
                                        )
                                    ],
                                    lg=12,
                                )
                            ],
                            style={"margin-top": "20px"},
                        ),
                    ]
                ),
            ]
        ),
    ]
)


# (1) Set postcode based on:
#     - URL (first load)
#     - map click
@callback(
    Output("postcode-selected", "value"),
    Input("url", "href"),
    Input("map", "clickData"),
    State("postcode-selected", "value"),
)
def update_dropdown(href, map_click_data, state_postcode):
    query_dict = parse_state(href)

    click_postcode = map_click_data["points"][0]["location"] if map_click_data else None

    # First load/blank URL query
    if state_postcode is None and click_postcode is None:
        if "postcode" in query_dict:
            return query_dict["postcode"]

    return click_postcode


# (2) Set URL based on postcode dropdown
@callback(
    Output("url", "search"),
    Input("postcode-selected", "value"),
    State("url", "search"),
)
def update_url_state(drop_postcode, url_search):

    if drop_postcode is None:
        if url_search:
            return ""
        else:
            return None

    state = urlencode(dict({"postcode": drop_postcode}))
    return f"?{state}"

@callback(
    Output("map", "figure"),
    Input("postcode-selected", "value"),
)
def update_map(postcode_selected):

    if postcode_selected:
        # https://github.com/geopandas/geopandas/issues/1051#issuecomment-585085721
        filtered_area = post_areas.loc[[postcode_selected]]
    else:
        filtered_area = post_areas

    bounds = filtered_area.total_bounds
    center_lon = (bounds[0] + bounds[2]) / 2
    center_lat = (bounds[1] + bounds[3]) / 2

    # https://stackoverflow.com/a/65043576
    max_bound = max(abs(bounds[2] - bounds[0]), abs(bounds[1] - bounds[3])) * 111
    zoom_level = 12 - np.log(max_bound)

    fig = px.choropleth_map(
        filtered_area,
        geojson=filtered_area.geometry,
        featureidkey = "id",
        locations=filtered_area.index,
        color="Registered Firearms",
        zoom=zoom_level,
        center={"lat": center_lat, "lon": center_lon},
        color_continuous_scale=px.colors.sequential.Viridis if len(filtered_area) > 1 else ['rgb(255,166,36)', 'rgb(255,166,36)'],
    )

    fig.update_traces(
        hovertemplate="<b>Postcode:</b> %{location}<br><b>Registered Firearms:</b> %{z}<extra></extra>"
    )

    return fig



# # (4) Set stats based on postcode dropdown
@callback(
    Output("postcode-stats", "children"),
    Input("postcode-selected", "value"),
)
def update_stats(postcode_selected):
    if postcode_selected and post_areas.loc[postcode_selected]["parse sucess"]:

        card_dict = {
            "Registered Firearms": post_areas.loc[postcode_selected][
                "Registered Firearms"
            ],
            "Registered Owners": post_areas.loc[postcode_selected][
                "Registered Firearms Owners"
            ],
            "Largest Stockpile": post_areas.loc[postcode_selected]["Largest stockpile"],
        }

        return [
            html.Hr(style={"margin-top": "0px"}),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4(
                                f"{k}",
                                style={
                                    "display": "inline",
                                    "padding-right": "16px",
                                },
                                className="align-middle",
                            ),
                            html.H2(
                                f"{int(v)}",
                                style={"display": "inline"},
                                className="align-middle",
                            ),
                        ],
                        lg=4,
                        style={
                            "text-align": "center",
                            "padding": "0px",
                        },
                    )
                    for k, v in card_dict.items()
                ],
                align="center",
                justify="center",
            ),
            html.Hr(),
        ]

    elif postcode_selected:
        return html.P(f"No data for postcode {postcode_selected}")
    else:
        return []
