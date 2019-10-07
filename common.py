from abc import ABC, abstractmethod

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

header = [
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(
                dbc.NavLink(
                    "About", href="/about", external_link=True
                )
            ),
        ],
        brand="Too Many Guns",
        brand_href="/",
        brand_external_link=True,
        color="dark",
        dark=True,
        # expand="lg",
    )
]


class BootstrapApp(dash.Dash, ABC):

    def __init__(self, name, server, url_base_pathname):

        external_stylesheets = [dbc.themes.BOOTSTRAP]

        super().__init__(
            name=name,
            server=server,
            url_base_pathname=url_base_pathname,
            external_stylesheets=external_stylesheets,
        )

        self.prelayout_setup()

        self.layout = html.Div(
            header
            + [
                dcc.Location(id="url", refresh=False),
                dbc.Container(
                    # Breadcrumbs
                    [
                        dbc.Nav(
                            [
                                html.Ol(
                                    [
                                        html.Li(
                                            html.A(
                                                crumb_tuple[0],
                                                href=crumb_tuple[1],
                                            ),
                                            className="breadcrumb-item",
                                        )
                                        for crumb_tuple in type(
                                            self
                                        ).breadcrumbs[:-1]
                                    ]
                                    + [
                                        html.Li(
                                            type(self).breadcrumbs[-1][0],
                                            className="breadcrumb-item active",
                                        )
                                    ],
                                    className="breadcrumb",
                                )
                            ],
                            navbar=True,
                        )
                    ]
                    # Content
                    + self.body() if type(self).breadcrumbs else self.body(),
                    style={'margin-top': "20px"}
                ),
            ]
        )

        self.postlayout_setup()

    @abstractmethod
    def body(self):
        pass

    def prelayout_setup(self):
        pass

    def postlayout_setup(self):
        pass

    @property
    @classmethod
    @abstractmethod
    def breadcrumbs(cls):
        return NotImplementedError


class MarkdownApp(BootstrapApp):
    @property
    @classmethod
    @abstractmethod
    def markdown(cls):
        return NotImplementedError

    def body(self):

        return [
            dbc.Row(
                dbc.Col(
                    dcc.Markdown(type(self).markdown),
                    lg=6
                ),
                justify="center"
            )
        ]
