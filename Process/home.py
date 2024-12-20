from dash import dcc, html, Input, Output
import calculate
from app import app

def get_indicator(change, base_value):
    # Genereert een indicator (pijl en kleur) voor verandering in waarde.
    if change is None or base_value == 0 or change == 0:
        return ""
    rounded_change = round(change, 1)  # Rond de verandering af op één decimaal.
    percent_change = (abs(change) / abs(base_value)) * 100  # Bereken de procentuele verandering.
    # Stel de kleur en pijlrichting in op basis van de verandering.
    color = "green" if change > 0 else "orange" if percent_change <= 15 else "red"
    arrow = "▲" if change > 0 else "▼"
    return html.Span(f"{arrow} {abs(rounded_change)}", style={"color": color, "margin-left": "5px"})

def generate_kpi_cards(period):
    # Genereert de KPI-kaarten voor de homepagina.
    changes = calculate.metrics.get(f'changes_{period}', {})  # Haal wijzigingen op voor de huidige periode.
    # Bepaal de vorige periode om veranderingen te berekenen.
    previous_period = 'day_before_yesterday' if period == 'yesterday' else 'two_weeks_ago'
    previous_metrics = calculate.metrics.get(previous_period, {})

    return html.Div(className="centered-containers", children=[
        # KPI-kaarten voor Infeed en Outfeed.
        html.A(href='/dashboard/InOut', className="container", children=[
            html.Div(className="kpi-card1", children=[
                html.H3("Infeed", className="kpi-title"),
                html.Hr(),
                html.P("Total Benches", className="kpi-subtitle"),
                html.Div([
                    # Toon totale invoer en eventuele veranderingen.
                    html.Span(calculate.metrics[period]['total_infeed'], className="kpi-value"),
                    get_indicator(changes.get('total_infeed'), previous_metrics.get('total_infeed', 1))
                ], style={"display": "inline-flex", "align-items": "center"})
            ]),
            html.Div(className="kpi-card1", children=[
                html.H3("Outfeed", className="kpi-title"),
                html.Hr(),
                html.P("Total Benches", className="kpi-subtitle"),
                html.Div([
                    # Toon totale uitvoer en eventuele veranderingen.
                    html.Span(calculate.metrics[period]['total_outfeed'], className="kpi-value"),
                    get_indicator(changes.get('total_outfeed'), previous_metrics.get('total_outfeed', 1))
                ], style={"display": "inline-flex", "align-items": "center"})
            ])
        ]),
        # KPI-kaarten voor de Harvester.
        html.A(href='/dashboard/harvester', className="container", children=[
            html.Div(className="kpi-card2", children=[
                html.H3("Harvester", className="kpi-title"),
                html.Hr(),
                html.P("Total KG Harvest", className="kpi-subtitle"),
                html.Div([
                    # Toon totaal geoogst gewicht en eventuele veranderingen.
                    html.Span(round(calculate.metrics[period]['total_harvest'], 1), className="kpi-value"),
                    get_indicator(changes.get('total_harvest'), previous_metrics.get('total_harvest', 1))
                ], style={"display": "inline-flex", "align-items": "center"}),
                html.Hr(),
                html.P("Harvested Benches", className="kpi-subtitle"),
                html.Div([
                    # Toon totale geoogste benches en eventuele veranderingen.
                    html.Span(calculate.metrics[period]['total_timestamps_bench_weight'], className="kpi-value"),
                    get_indicator(changes.get('total_timestamps_bench_weight'), previous_metrics.get('total_timestamps_bench_weight', 1))
                ], style={"display": "inline-flex", "align-items": "center"}),
                html.Hr(),
                html.P("Average yield[KG/Bench]", className="kpi-subtitle"),
                html.Div([
                    # Toon gemiddelde opbrengst en eventuele veranderingen.
                    html.Span(round(calculate.metrics[period]['average_yield'], 2), className="kpi-value"),
                    get_indicator(changes.get('average_yield'), previous_metrics.get('average_yield', 1))
                ], style={"display": "inline-flex", "align-items": "center"})
            ]),
        ])
    ])

# Layout voor de homepagina.
layout = html.Div([
    html.Div(id='content')  # Lege container voor dynamische inhoud.
])

@app.callback(
    Output('content', 'children'),  # Output naar de 'content' container.
    [Input('selected-period', 'data')]  # Input: de geselecteerde periode.
)
def update_home_content(period):
    # Update de inhoud van de homepagina op basis van de geselecteerde periode.
    return generate_kpi_cards(period)
