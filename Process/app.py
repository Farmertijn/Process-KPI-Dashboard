from dash import Dash  # Importeer de Dash-klasse voor het bouwen van de applicatie.

external_stylesheets = ['/assets/styles.css']  # Verwijs naar een extern CSS-bestand voor styling.

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
# Maak een Dash-applicatie met externe stylesheets en ondersteuning voor dynamische callbacks.

server = app.server  # Maak de onderliggende Flask-server beschikbaar.
