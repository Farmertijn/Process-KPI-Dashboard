import subprocess
import sys
from datetime import timedelta, datetime
import pandas as pd
from dash import dcc, html, Input, Output, State, callback_context
from app import app, server
import home
import InOut
import harvester
import calculate
from data import df_filling_infeed, df_bench_weight, df_transplanting_infeed, using_csv_backup, reference_date  # Importeer referentiedatum

# Lijst met benodigde libraries
required_libraries = [
    "dash",
    "dash_bootstrap_components",
    "mariadb",
    "pandas",
    "pytz",
    "seaborn",
    "matplotlib",
    "sqlalchemy"
]

# Controleer en installeer ontbrekende libraries
for library in required_libraries:
    try:
        __import__(library)
    except ImportError:
        print(f"{library} wordt geïnstalleerd...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", library])

# Layout met centrale knoppen en exportknop
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='selected-period', data='today'),
    html.Div(className='button-container', children=[
        html.Button('Today', id='btn-today', className='tab-button', n_clicks=0),
        html.Button('Yesterday', id='btn-yesterday', className='tab-button', n_clicks=0),
        html.Button('Last Week', id='btn-week', className='tab-button', n_clicks=0),
        html.Button("Export Data to CSV", id="export-btn", className='tab-button', n_clicks=0),
        dcc.Download(id="data-download")
    ]),
    html.Div(id='page-content')
])

# Callback voor navigatie naar de juiste pagina (InOut, Harvester of Home)
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('selected-period', 'data')]
)
def display_page(pathname, period):
    if pathname == '/' or pathname == '/home':
        return home.generate_kpi_cards(period)
    elif pathname == '/InOut':
        return InOut.generate_inout_kpi_cards(period)
    elif pathname == '/harvester':
        return harvester.generate_harvester_kpi_cards(period)
    else:
        return '404'

# Callback voor de knoppen om de periode in te stellen
@app.callback(
    [Output('selected-period', 'data'),
     Output('btn-today', 'className'),
     Output('btn-yesterday', 'className'),
     Output('btn-week', 'className')],
    [Input('btn-today', 'n_clicks'),
     Input('btn-yesterday', 'n_clicks'),
     Input('btn-week', 'n_clicks')]
)
def update_button_styles(n_clicks_today, n_clicks_yesterday, n_clicks_week):
    ctx = callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'btn-today'

    period_map = {
        'btn-today': 'today',
        'btn-yesterday': 'yesterday',
        'btn-week': 'week'
    }
    period = period_map.get(button_id, 'today')

    return (
        period,
        'tab-button active' if button_id == 'btn-today' else 'tab-button',
        'tab-button active' if button_id == 'btn-yesterday' else 'tab-button',
        'tab-button active' if button_id == 'btn-week' else 'tab-button'
    )


def filter_data_by_period(df, period):
    if 'timestamp' not in df.columns:
        raise ValueError("De dataframe bevat geen 'timestamp' kolom. Controleer de kolomnamen.")

    # Zet de timestamp kolom om naar datetime, indien nodig
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # Bepaal de huidige tijd, afhankelijk van de bron (database of CSV)
    current_time = reference_date if using_csv_backup else datetime.now()

    # Controleer of de timestamp kolom een tijdzone bevat en pas aan als dat zo is
    if df['timestamp'].dt.tz is not None:
        tz_info = df['timestamp'].dt.tz
        current_time = current_time.replace(tzinfo=tz_info)
    else:
        tz_info = None

    # Instellen van start- en eindtijden op basis van de periode
    if period == 'today':
        start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)

    elif period == 'yesterday':
        start_time = (current_time - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)

    elif period == 'week':
        start_time = (current_time - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = current_time

    # Breng start_time en end_time in dezelfde tijdzone als timestamp indien nodig
    if tz_info:
        start_time = start_time.astimezone(tz_info)
        end_time = end_time.astimezone(tz_info)

    # Pas filtering toe op basis van periode
    return df[(df['timestamp'] >= start_time) & (df['timestamp'] < end_time)]

@app.callback(
    [Output("data-download", "data"), Output("export-btn", "n_clicks")],
    [Input("export-btn", "n_clicks")],
    [State("url", "pathname"), State("selected-period", "data")],
    prevent_initial_call=True
)
def export_data(n_clicks, pathname, period):
    if n_clicks is None or n_clicks == 0:
        return None, 0  # Reset n_clicks en voer geen download uit

    data = None
    filename = "data.csv"

    if pathname == '/InOut':
        # Filter de filling infeed en transplanting infeed data voor de geselecteerde periode
        filtered_filling_infeed = filter_data_by_period(df_filling_infeed.copy(), period)
        filtered_transplanting_infeed = filter_data_by_period(df_transplanting_infeed.copy(), period)

        # Combineer beide DataFrames op basis van timestamp
        combined_df = pd.concat([filtered_filling_infeed, filtered_transplanting_infeed]).sort_values(by='timestamp')
        filename = f"inout_raw_data_{period}.csv"
        data = dcc.send_data_frame(combined_df.to_csv, filename)

    elif pathname == '/harvester':
        # Filter de bench weight data voor de geselecteerde periode
        filtered_df = filter_data_by_period(df_bench_weight.copy(), period)
        filename = f"harvester_raw_data_{period}.csv"
        data = dcc.send_data_frame(filtered_df.to_csv, filename)

    return data, 0  # Reset n_clicks direct na export


if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port=8050, debug=False)
