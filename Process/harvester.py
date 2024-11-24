from dash import html, Input, Output
import calculate
import charts
from app import app

def generate_harvester_kpi_cards(period):
    total_harvest = round(calculate.metrics[period]['total_harvest'], 1)
    harvested_benches = calculate.metrics[period]['total_timestamps_bench_weight']
    average_yield = round(calculate.metrics[period]['average_yield'], 2)
    bench_weight_data = calculate.metrics[period]['data_bench_weight']

    encoded_harvested_benches_image = charts.generate_harvested_benches_chart(bench_weight_data)
    encoded_harvested_weight_image = charts.generate_harvested_weight_chart(bench_weight_data)
    encoded_average_yield_image = charts.generate_average_yield_chart(bench_weight_data)
    encoded_total_harvest_chart = charts.generate_total_harvest_chart(bench_weight_data, period) if period == 'week' else None
    encoded_harvested_benches_week_image = charts.generate_harvested_benches_week_chart(bench_weight_data, period) if period == 'week' else None
    encoded_average_yield_week_chart = charts.generate_average_yield_week_chart(bench_weight_data, period) if period == 'week' else None

    container_class = "container-inout-double" if period == 'week' else "container-inout"
    container_class_img = "kpi-card5" if period == 'week' else 'kpi-card4'

    return html.Div(className="centered-containers", children=[
        html.Div(className=container_class, children=[
            html.Div(className="kpi-card3", children=[
                html.H3("Total KG Harvest", className="kpi-title-inout"),
                html.P(total_harvest, className="kpi-value-inout")
            ]),
            html.Div(className=container_class_img, children=[
                html.Img(src=f'data:image/png;base64,{encoded_harvested_weight_image}') if encoded_harvested_weight_image else html.P("No data available for the selected period.")
            ]),
            html.Div(className=container_class_img, children=[
                html.Img(src=f'data:image/png;base64,{encoded_total_harvest_chart}') if encoded_total_harvest_chart else None
            ]) if period == 'week' else None
        ]),
        html.Div(className=container_class, children=[
            html.Div(className="kpi-card3", children=[
                html.H3("Harvested Benches", className="kpi-title-inout"),
                html.P(harvested_benches, className="kpi-value-inout")
            ]),
            html.Div(className=container_class_img, children=[
                html.Img(src=f'data:image/png;base64,{encoded_harvested_benches_image}') if encoded_harvested_benches_image else html.P("No data available for the selected period.") 
            ]),
            html.Div(className=container_class_img, children=[
                html.Img(src=f'data:image/png;base64,{encoded_harvested_benches_week_image}') if encoded_harvested_benches_week_image else None
            ]) if period == 'week' else None
        ]),
        html.Div(className=container_class, children=[
            html.Div(className="kpi-card3", children=[
                html.H3("Average Yield [KG/Bench]", className="kpi-title-inout"),
                html.P(average_yield, className="kpi-value-inout")
            ]),
            html.Div(className=container_class_img, children=[
                html.Img(src=f'data:image/png;base64,{encoded_average_yield_image}') if encoded_average_yield_image else html.P("No data available for the selected period.") 
            ]),
            html.Div(className=container_class_img, children=[
                html.Img(src=f'data:image/png;base64,{encoded_average_yield_week_chart}') if encoded_average_yield_week_chart else None
            ]) if period == 'week' else None
        ]),
    ])

layout = html.Div([
    html.Div(id='content-harvester')
])

@app.callback(
    Output('content-harvester', 'children'),
    [Input('selected-period', 'data')]
)
def update_harvester_content(period):
    return generate_harvester_kpi_cards(period)
