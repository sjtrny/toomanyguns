from datetime import date

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

dash.register_page(__name__, path="/about", title="About | Too Many Guns")

current_year = date.today().year

layout = html.Div(
    [
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
                        [
                            dcc.Markdown(
                                f"""
                    ## About
                    ----
                    This website shows ownership of firearms in NSW by postcode. This information has been made public thanks to the NSW Greens through a FOI request to NSW Police.

                    ## FAQ
                    ----

                    ##### Doesn't toomanyguns.org already exist?

                    Yes, but it could be better. It's {current_year} and they don't even [use HTTPS](https://doesmysiteneedhttps.com/)!

                    ##### This doesn't work on my computer/browser?

                    It's best viewed on a modern browser such as Safari or Chrome with graphics acceleration enabled.

                    ##### How did you make this?

                    This website is built on [Dash for Python](https://github.com/plotly/dash).

                    You can find the code on [Github](https://github.com/sjtrny/toomanyguns)

                    ##### Who made this?

                    I did, you can find more details on my website [sjtrny.com](https://sjtrny.com)

                    ## Data
                    ----

                    ##### Postcode Information

                    Sourced from [https://www.matthewproctor.com/australian_postcodes](https://www.matthewproctor.com/australian_postcodes)

                    ##### Postal Area Geography Data

                    This information is available from the ABS under the listing [1270.0.55.003 - Australian Statistical Geography Standard (ASGS): Volume 3 - Non ABS Structures, July 2016](https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/1270.0.55.003July%202016?OpenDocument)

                    The specific file used is titled "Postal Areas ASGS Ed 2016 Digital Boundaries in ESRI Shapefile Format"

                    ##### Firearms Data

                    I did my best to scrape [http://toomanyguns.org](http://toomanyguns.org).

                    [Click here to download the data](/assets/firearms_2019.csv).
                    """
                            ),
                        ]
                    )
                )
            ]
        ),
    ]
)
