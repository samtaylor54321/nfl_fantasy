import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

df = pd.read_csv("output.csv")

df = df.fillna(0)

colors = {"background": "#111111", "text": "#7FDBFF"}

app.layout = html.Div(
    style={"backgroundColor": colors["background"]},
    children=[
        html.H1(
            children="Hello Dash",
            style={"textAlign": "center", "color": colors["text"]},
        ),
        html.Div(
            children="Dash: A web application framework for your data.",
            style={"textAlign": "center", "color": colors["text"]},
        ),
        html.Br(),
        html.Label("Multi-Select Dropdown"),
        dcc.Dropdown(
            id="Positions",
            options=["QB", "RB", "WR", "TE", "K", "DST"],
            multi=True,
        ),
        dcc.Graph(
            id="example-graph-2",
        ),
    ],
)


@app.callback(Output("example-graph-2", "figure"), Input("Positions", "value"))
def update_figure(selected_year):
    filtered_df = df  # df[df.position_x == selected_year]

    fig = px.scatter(
        filtered_df,
        x="overall_pts",
        y="Value",
        color="Position",
        trendline="ols",
        hover_name="Player",
    )

    fig.update_layout(
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        transition_duration=500,
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
