import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    external_scripts=[
        "https://cdn.jsdelivr.net/npm/bs-breakpoints/dist/bs-breakpoints.min.js"
    ],
    use_pages=True,
)
server = app.server
app.layout = dash.page_container

if __name__ == "__main__":
    app.run_server(debug=True)
