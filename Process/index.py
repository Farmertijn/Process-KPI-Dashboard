from dash import dcc, html, Input, Output, callback_context
from app import app, server
import home
import InOut
import harvester
import pandas as pd
import calculate

# Layout met centrale knoppen en exportknop
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='selected-period', data='today'),
    html.Div(className='button-container', children=[
        html.Button('Today', id='btn-today', className='tab-button', n_clicks=0),
        html.Button('Yesterday', id='btn-yesterday', className='tab-button', n_clicks=0),
        html.Button('Last Week', id='btn-week', className='tab-button', n_clicks=0),
        html.Button("Export Data to CSV", id="export-btn"),  # Export knop toegevoegd
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

# Callback voor de export-knop
@app.callback(
    Output("data-download", "data"),
    [Input("export-btn", "n_clicks"),
     Input("url", "pathname"),
     Input('selected-period', 'data')],
    prevent_initial_call=True
)
def export_data(n_clicks, pathname, period):
    data = None
    filename = "data.csv"

    if pathname == '/InOut':
        # InOut data exporteren
        inout_data = calculate.metrics.get(period, {})
        if inout_data:
            df = pd.DataFrame({
                'Transplanting Infeed': [inout_data['total_timestamps_transplanting_infeed']],
                'Filling Infeed': [inout_data['total_timestamps_filling_infeed']],
                'Outfeed Benches to Harvester': [inout_data['total_timestamps_bench_weight']],
                'Outfeed Benches to Transplanting': [inout_data['total_outfeed'] - inout_data['total_timestamps_bench_weight']]
            })
            filename = f"inout_data_{period}.csv"
            data = dcc.send_data_frame(df.to_csv, filename)
    
    elif pathname == '/harvester':
        # Harvester data exporteren
        harvester_data = calculate.metrics.get(period, {})
        if harvester_data:
            df = pd.DataFrame({
                'Total Harvest (KG)': [harvester_data['total_harvest']],
                'Harvested Benches': [harvester_data['total_timestamps_bench_weight']],
                'Average Yield (KG/Bench)': [harvester_data['average_yield']]
            })
            filename = f"harvester_data_{period}.csv"
            data = dcc.send_data_frame(df.to_csv, filename)
    
    return data
