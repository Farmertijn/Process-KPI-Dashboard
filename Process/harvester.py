from dash import html, Input, Output
import calculate
import charts
from app import app

def generate_harvester_kpi_cards(period):
    # Genereer KPI-kaarten en grafieken voor de harvester dashboard.
    total_harvest = round(calculate.metrics[period]['total_harvest'], 1)  # Totale geoogste kilogrammen.
    harvested_benches = calculate.metrics[period]['total_timestamps_bench_weight']  # Aantal geoogste benches.
    average_yield = round(calculate.metrics[period]['average_yield'], 2)  # Gemiddelde opbrengst per bench.
    bench_weight_data = calculate.metrics[period]['data_bench_weight']  # Bench-gewicht gegevens.

    # Genereer afbeeldingen van grafieken als base64-strings.
    encoded_harvested_benches_image = charts.generate_harvested_benches_chart(bench_weight_data)
    encoded_harvested_weight_image = charts.generate_harvested_weight_chart(bench_weight_data)
    encoded_average_yield_image = charts.generate_average_yield_chart(bench_weight_data)
    encoded_total_harvest_chart = charts.generate_total_harvest_chart(bench_weight_data, period) if period == 'week' else None
    encoded_harvested_benches_week_image = charts.generate_harvested_benches_week_chart(bench_weight_data, period) if period == 'week' else None
    encoded_average_yield_week_chart = charts.generate_average_yield_week_chart(bench_weight_data, period) if period == 'week' else None

    # Pas de containerklassen aan afhankelijk van de geselecteerde periode.
    container_class = "container-inout-double" if period == 'week' else "container-inout"
    container_class_img = "kpi-card5" if period == 'week' else 'kpi-card4'

    # Bouw de KPI-kaarten op.
    return html.Div(className="centered-containers", children=[
        html.Div(className=container_class, children=[
            html.Div(className="kpi-card3", children=[
                html.H3("Total KG Harvest", className="kpi-title-inout"),
                html.P(total_harvest, className="kpi-value-inout")  # Toon totaal geoogst gewicht.
            ]),
            html.Div(className=container_class_img, children=[
                html.Img(src=f'data:image/png;base64,{encoded_harvested_weight_image}') if encoded_harvested_weight_image else html.P("No data available for the selected period.")
            ]),
            html.Div(className=container_class_img, children=[
                html.Img(src=f'data:image/png;base64,{encoded_total_harvest_chart}') if encoded_total_harvest_chart else None
            ]) if period == 'week' else None  # Toon specifieke grafiek voor een week.
        ]),
        html.Div(className=container_class, children=[
            html.Div(className="kpi-card3", children=[
                html.H3("Harvested Benches", className="kpi-title-inout"),
                html.P(harvested_benches, className="kpi-value-inout")  # Toon aantal geoogste benches.
            ]),
            html.Div(className=container_class_img, children=[
                html.Img(src=f'data:image/png;base64,{encoded_harvested_benches_image}') if encoded_harvested_benches_image else html.P("No data available for the selected period.")
            ]),
            html.Div(className=container_class_img, children=[
                html.Img(src=f'data:image/png;base64,{encoded_harvested_benches_week_image}') if encoded_harvested_benches_week_image else None
            ]) if period == 'week' else None  # Week specifieke grafiek.
        ]),
        html.Div(className=container_class, children=[
            html.Div(className="kpi-card3", children=[
                html.H3("Average Yield [KG/Bench]", className="kpi-title-inout"),
                html.P(average_yield, className="kpi-value-inout")  # Toon gemiddelde opbrengst per bench.
            ]),
            html.Div(className=container_class_img, children=[
                html.Img(src=f'data:image/png;base64,{encoded_average_yield_image}') if encoded_average_yield_image else html.P("No data available for the selected period.")
            ]),
            html.Div(className=container_class_img, children=[
                html.Img(src=f'data:image/png;base64,{encoded_average_yield_week_chart}') if encoded_average_yield_week_chart else None
            ]) if period == 'week' else None  # Toon gemiddelde weekgrafiek.
        ]),
    ])

# Layout voor de harvester sectie.
layout = html.Div([
    html.Div(id='content-harvester')  # Container voor dynamische inhoud.
])

@app.callback(
    Output('content-harvester', 'children'),  # Output voor het harvester-content element.
    [Input('selected-period', 'data')]  # Input: geselecteerde periode.
)
def update_harvester_content(period):
    # Update de inhoud van de harvester-sectie op basis van de geselecteerde periode.
    return generate_harvester_kpi_cards(period)