from dash import html, Input, Output
import calculate
import charts
from app import app
import pandas as pd

def generate_inout_kpi_cards(period):
    half_hourly_data = calculate.metrics[period]['transplanting_infeed_15MIN']
    filling_infeed_data = calculate.metrics[period]['data_filling_infeed']
    total_outfeed_data = calculate.metrics[period]['outfeed_15MIN']
    bench_weight_15MIN = calculate.metrics[period]['data_bench_weight_15MIN']
    unique_transplant_jobs_15MIN = calculate.metrics[period]['unique_transplant_jobs_15MIN']

    encoded_image = charts.generate_transplanting_infeed_chart(half_hourly_data, period)
    encoded_bar_image = charts.generate_filling_infeed_chart(filling_infeed_data)
    encoded_outfeed_image = charts.generate_outfeed_chart(total_outfeed_data, period, bench_weight_15MIN, unique_transplant_jobs_15MIN)

    total_timestamps_bench_weight = calculate.metrics[period]['total_timestamps_bench_weight']
    unique_transplant_jobs = calculate.metrics[period]['total_outfeed'] - total_timestamps_bench_weight
    
    return html.Div(className="centered-containers", children=[
        html.Div(className="container-inout", children=[
            html.Div(className="kpi-card3", children=[
                html.H3("Transplanting Infeed", className="kpi-title-inout"),
                html.P(calculate.metrics[period]['total_timestamps_transplanting_infeed'], className="kpi-value-inout"),
            ]),
            html.Div(children=[
                html.Img(src=f'data:image/png;base64,{encoded_image}') if encoded_image else html.P("No data available for the selected period.")
            ], className="kpi-card4")
        ]),
        html.Div(className="container-inout", children=[
            html.Div(className="kpi-card3", children=[
                html.H3("Filling Infeed", className="kpi-title-inout"),
                html.P(calculate.metrics[period]['total_timestamps_filling_infeed'], className="kpi-value-inout")
            ]),
            html.Div(className="kpi-card4", children=[
                html.Img(src=f'data:image/png;base64,{encoded_bar_image}') if encoded_bar_image else html.P("No data available for the selected period.")
            ])
        ]),
        html.Div(className="container-inout", children=[
            html.Div(className="kpi-card3", children=[
                html.H3("Outfeed Benches", className="kpi-title-inout"),
                html.Div(className="kpi-value-inout-outfeed", children=[
                    html.Div(style={"text-align": "center"}, children=[
                        html.Span("To Harvester", className="kpi-subtitle"),
                        html.Span(f"{total_timestamps_bench_weight}", style={"color": "#555", "fontSize": "30px"})
                    ]),
                    html.Span(f"{calculate.metrics[period]['total_outfeed']}"),
                    html.Div(style={"text-align": "center"}, children=[
                        html.Span("To Transplanting", className="kpi-subtitle"),
                        html.Span(f"{unique_transplant_jobs}", style={"color": "#555", "fontSize": "30px"})
                    ])
                ])
            ]),
            html.Div(className="kpi-card4", children=[
                html.Img(src=f'data:image/png;base64,{encoded_outfeed_image}') if encoded_outfeed_image else html.P("No data available for the selected period.")
            ])
        ])
    ])

layout = html.Div([
    html.Div(id='content-inout')
])

@app.callback(
    Output('content-inout', 'children'),
    [Input('selected-period', 'data')]
)
def update_inout_content(period):
    return generate_inout_kpi_cards(period)
