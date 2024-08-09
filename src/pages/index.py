import json
from sys import getsizeof
from urllib.parse import parse_qsl, urlencode, urlparse

import dash
import dash_bootstrap_components as dbc
import geopandas as gpd
from dash import Input, Output, State, callback, dcc, html
from dash.dependencies import ClientsideFunction, Input, Output, State
from hurry.filesize import size


def parse_state(url):
    parse_result = urlparse(url)
    params = parse_qsl(parse_result.query)
    state = dict(params)
    return state


dash.register_page(__name__, path="/", title="Too Many Guns")

token = "pk.eyJ1Ijoic2p0cm55IiwiYSI6ImNrMWJrOGlueTA1ZzMzbHBjeGdtOTN4MHUifQ.V20gMVX6fBu3kyWZaMpI_g"

file = open("data_generated/nsw.json")
json_str = file.read()
file.close()

post_areas_json = json.loads(json_str)
print(size(getsizeof(json_str)))

post_areas = gpd.read_file(json_str)
post_areas = post_areas.set_index("id", drop=False)
post_areas = post_areas.dropna()

hover_text = [
    f"Postcode: {index}<br>" f"Firearms: {int(row['Registered Firearms'])}"
    for index, row in post_areas.iterrows()
]

fig_data = {
    "type": "choroplethmapbox",
    "geojson": post_areas_json,
    "locations": list(post_areas["id"]),
    "z": list(post_areas["Registered Firearms"]),
    "text": hover_text,
    "hoverinfo": "text",
    "colorscale": "Viridis",
    "colorbar": {"title": "Firearms"},
    "marker": dict(opacity=0.5, line=dict(width=1)),
}

layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(html.A("About", href="/about", className="nav-link")),
            ],
            brand="Too Many Guns",
            brand_href="/",
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
                        dcc.Store(id="fig-data"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Graph(
                                            id="mapbox",
                                            config={
                                                "displayModeBar": False,
                                                "mapboxAccessToken": token,
                                                "responsive": True,
                                            },
                                            style={
                                                "height": "60vh",
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


# Set the children of fig_data to be the JSON
@callback(Output("fig-data", "data"), [Input("url", "href")])
def load_data(href):
    return fig_data


# (1) Set postcode based on:
#     - URL (first load)
#     - map click
@callback(
    Output("postcode-selected", "value"),
    Input("url", "href"),
    Input("mapbox", "clickData"),
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


# (3) Set figure based on postcode dropdown
dash.clientside_callback(
    ClientsideFunction("clientside", "figure"),
    Output("mapbox", "figure"),
    Input("fig-data", "data"),
    Input("postcode-selected", "value"),
)


# (4) Set stats based on postcode dropdown
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
