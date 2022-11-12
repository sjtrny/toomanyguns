import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)
server = app.server
app.layout = dash.page_container

if __name__ == "__main__":
    app.run_server(debug=True)
