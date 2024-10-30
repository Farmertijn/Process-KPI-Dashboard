from dash import Dash
import dash_bootstrap_components as dbc

external_stylesheets = ['https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css', '/assets/styles.css']

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server