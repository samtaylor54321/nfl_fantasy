import dash_auth
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go

from src.scrapper import NFLDataScrapper
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

# Set environment variables
VALID_USERNAME_PASSWORD_PAIRS = {os.getenv("API_USER"): os.environ.get("API_PASSWORD")}

app = Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
)

auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

# Instantiate scrapper
scraper = NFLDataScrapper()

# Scrape player data
all_players = scraper.generate_nfl_dataset()

players_long = (
    all_players.iloc[:, 0:14]
    .melt(id_vars=["Name", "Position"])
    .sort_values(["Name", "variable"])
)

players_long["shifted"] = players_long.groupby(["Name", "Position"])["value"].shift(1)

players_long = players_long.fillna(0)

players_long["weekly_points"] = players_long["value"].astype(float) - players_long[
    "shifted"
].astype(float)

player_params = players_long.groupby(["Name"])["weekly_points"].agg([np.mean, np.std])

fig1 = px.scatter(
    all_players,
    x="Price",
    y="AvgPoints",
    color="Position",
    facet_col="Free Agent",
    size="Years Remaining",
    trendline="ols",
    hover_name="Name",
    hover_data=["Team", "Years Remaining"],
    labels={"4": "Total Points Score", "Price": "Price"},
)
fig1.add_hline(y=all_players["AvgPoints"].mean(), line_dash="dot")
fig1.add_vline(x=all_players["Price"].mean(), line_dash="dot")
fig1.update_traces(
    marker=dict(line=dict(width=2, color="DarkSlateGrey")),
    selector=dict(mode="markers"),
)
fig1.update_xaxes(matches=None)

fig2 = px.scatter(
    all_players,
    x="Price",
    y="Trade Value",
    color="Position",
    facet_col="Free Agent",
    size="Years Remaining",
    trendline="ols",
    hover_name="Name",
    hover_data=["Team", "Years Remaining"],
    labels={"4": "Total Points Score", "Price": "Price"},
)
fig2.add_hline(y=all_players["Trade Value"].mean(), line_dash="dot")
fig2.add_vline(x=all_players["Price"].mean(), line_dash="dot")
fig2.update_traces(
    marker=dict(line=dict(width=2, color="DarkSlateGrey")),
    selector=dict(mode="markers"),
)
fig2.update_xaxes(matches=None)

fig3 = px.scatter(
    all_players,
    x="AvgPoints",
    y="Trade Value",
    color="Position",
    facet_col="Free Agent",
    size="Years Remaining",
    trendline="ols",
    hover_name="Name",
    hover_data=["Team", "Years Remaining"],
    labels={"4": "Total Points Score", "Price": "Price"},
)
fig3.add_hline(y=all_players["Trade Value"].mean(), line_dash="dot")
fig3.add_vline(x=all_players["AvgPoints"].mean(), line_dash="dot")
fig3.update_traces(
    marker=dict(line=dict(width=2, color="DarkSlateGrey")),
    selector=dict(mode="markers"),
)
fig3.update_xaxes(matches=None)

app.layout = html.Div(
    [
        html.H1("NFL Fantasy Dashboard"),
        dcc.Tabs(
            id="tabs-example-graph",
            value="tab-1-example-graph",
            children=[
                dcc.Tab(label="Free Agent Evaluator", value="tab-1-example-graph"),
                dcc.Tab(label="Line Up Evaluator", value="tab-2-example-graph"),
            ],
        ),
        html.Div(id="tabs-content-example-graph"),
    ]
)


@app.callback(
    Output("tabs-content-example-graph", "children"),
    Input("tabs-example-graph", "value"),
)
def render_content(tab):
    if tab == "tab-1-example-graph":
        return html.Div(
            [dcc.Graph(figure=fig1), dcc.Graph(figure=fig2), dcc.Graph(figure=fig3)]
        )
    elif tab == "tab-2-example-graph":
        return html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(
                            id="graph-2-tabs-dcc",
                        ),
                    ],
                    style={"width": "1600px", "height": "500px"},
                ),
                html.Div(
                    [
                        html.H3("Original Line Up"),
                        html.H5("QB"),
                        dcc.Dropdown(
                            id="qb_dropdown",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "QB")
                                ]["Name"]
                            ],
                        ),
                        html.H5("RB"),
                        dcc.Dropdown(
                            id="rb1_dropdown",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "RB")
                                ]["Name"]
                            ],
                        ),
                        html.H5("RB"),
                        dcc.Dropdown(
                            id="rb2_dropdown",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "RB")
                                ]["Name"]
                            ],
                        ),
                        html.H5("WR"),
                        dcc.Dropdown(
                            id="wr1_dropdown",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "WR")
                                ]["Name"]
                            ],
                        ),
                        html.H5("WR"),
                        dcc.Dropdown(
                            id="wr2_dropdown",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "WR")
                                ]["Name"]
                            ],
                        ),
                        html.H5("WR"),
                        dcc.Dropdown(
                            id="wr3_dropdown",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "WR")
                                ]["Name"]
                            ],
                        ),
                        html.H5("TE"),
                        dcc.Dropdown(
                            id="te_dropdown",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "TE")
                                ]["Name"]
                            ],
                        ),
                        html.H5("Flex"),
                        dcc.Dropdown(
                            id="flex_dropdown",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (
                                        (all_players["Position"] == "RB")
                                        | (all_players["Position"] == "WR")
                                        | (all_players["Position"] == "TE")
                                    )
                                ]["Name"]
                            ],
                        ),
                        html.H5("K"),
                        dcc.Dropdown(
                            id="k_dropdown",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "K")
                                ]["Name"]
                            ],
                        ),
                        html.H5("DST"),
                        dcc.Dropdown(
                            id="dst_dropdown",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "DST")
                                ]["Name"]
                            ],
                        ),
                    ],
                    style={"display": "inline-block", "width": "800px"},
                ),
                html.Div(
                    [
                        html.H3("Alternative Line Up"),
                        html.H5("QB"),
                        dcc.Dropdown(
                            id="qb_dropdown_alt",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "QB")
                                ]["Name"]
                            ],
                        ),
                        html.H5("RB"),
                        dcc.Dropdown(
                            id="rb1_dropdown_alt",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "RB")
                                ]["Name"]
                            ],
                        ),
                        html.H5("RB"),
                        dcc.Dropdown(
                            id="rb2_dropdown_alt",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "RB")
                                ]["Name"]
                            ],
                        ),
                        html.H5("WR"),
                        dcc.Dropdown(
                            id="wr1_dropdown_alt",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "WR")
                                ]["Name"]
                            ],
                        ),
                        html.H5("WR"),
                        dcc.Dropdown(
                            id="wr2_dropdown_alt",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "WR")
                                ]["Name"]
                            ],
                        ),
                        html.H5("WR"),
                        dcc.Dropdown(
                            id="wr3_dropdown_alt",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "WR")
                                ]["Name"]
                            ],
                        ),
                        html.H5("TE"),
                        dcc.Dropdown(
                            id="te_dropdown_alt",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "TE")
                                ]["Name"]
                            ],
                        ),
                        html.H5("Flex"),
                        dcc.Dropdown(
                            id="flex_dropdown_alt",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (
                                        (all_players["Position"] == "RB")
                                        | (all_players["Position"] == "WR")
                                        | (all_players["Position"] == "TE")
                                    )
                                ]["Name"]
                            ],
                        ),
                        html.H5("K"),
                        dcc.Dropdown(
                            id="k_dropdown_alt",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "K")
                                ]["Name"]
                            ],
                        ),
                        html.H5("DST"),
                        dcc.Dropdown(
                            id="dst_dropdown_alt",
                            options=[
                                {"label": player, "value": player}
                                for player in all_players[
                                    (all_players["Team"] == "Tottenham Royals")
                                    & (all_players["Position"] == "DST")
                                ]["Name"]
                            ],
                        ),
                    ],
                    style={"display": "inline-block", "width": "800px"},
                ),
            ]
        )


@app.callback(
    Output("graph-2-tabs-dcc", "figure"),
    Input("qb_dropdown", "value"),
    Input("rb1_dropdown", "value"),
    Input("rb2_dropdown", "value"),
    Input("wr1_dropdown", "value"),
    Input("wr2_dropdown", "value"),
    Input("wr3_dropdown", "value"),
    Input("te_dropdown", "value"),
    Input("flex_dropdown", "value"),
    Input("dst_dropdown", "value"),
    Input("k_dropdown", "value"),
    Input("qb_dropdown_alt", "value"),
    Input("rb1_dropdown_alt", "value"),
    Input("rb2_dropdown_alt", "value"),
    Input("wr1_dropdown_alt", "value"),
    Input("wr2_dropdown_alt", "value"),
    Input("wr3_dropdown_alt", "value"),
    Input("te_dropdown_alt", "value"),
    Input("flex_dropdown_alt", "value"),
    Input("dst_dropdown_alt", "value"),
    Input("k_dropdown_alt", "value"),
)
def update_plot(
    qb_dropdown,
    rb1_dropdown,
    rb2_dropdown,
    wr1_dropdown,
    wr2_dropdown,
    wr3_dropdown,
    te_dropdown,
    flex_dropdown,
    dst_dropdown,
    k_dropdown,
    qb_dropdown_alt,
    rb1_dropdown_alt,
    rb2_dropdown_alt,
    wr1_dropdown_alt,
    wr2_dropdown_alt,
    wr3_dropdown_alt,
    te_dropdown_alt,
    flex_dropdown_alt,
    dst_dropdown_alt,
    k_dropdown_alt,
):

    if dst_dropdown_alt:

        score_dist = []
        score_dist_alt = []

        for _ in range(10000):

            qb_score = np.random.exponential(
                player_params.loc[qb_dropdown, "mean"],
            )
            rb1_score = np.random.exponential(
                player_params.loc[rb1_dropdown, "mean"],
            )
            rb2_score = np.random.exponential(
                player_params.loc[rb2_dropdown, "mean"],
            )
            wr1_score = np.random.exponential(
                player_params.loc[wr1_dropdown, "mean"],
            )
            wr2_score = np.random.exponential(
                player_params.loc[wr2_dropdown, "mean"],
            )
            wr3_score = np.random.exponential(
                player_params.loc[wr3_dropdown, "mean"],
            )
            te_score = np.random.exponential(
                player_params.loc[te_dropdown, "mean"],
            )
            flex_score = np.random.exponential(
                player_params.loc[flex_dropdown, "mean"],
            )
            kicker_score = np.random.exponential(
                player_params.loc[k_dropdown, "mean"],
            )
            dst_score = np.random.exponential(
                player_params.loc[dst_dropdown, "mean"],
            )

            total_score = (
                qb_score
                + rb1_score
                + rb2_score
                + wr1_score
                + wr2_score
                + wr3_score
                + te_score
                + flex_score
                + kicker_score
                + dst_score
            )

            score_dist.append(total_score)

            qb_score_alt = np.random.exponential(
                player_params.loc[qb_dropdown_alt, "mean"],
            )
            rb1_score_alt = np.random.exponential(
                player_params.loc[rb1_dropdown_alt, "mean"],
            )
            rb2_score_alt = np.random.exponential(
                player_params.loc[rb2_dropdown_alt, "mean"],
            )
            wr1_score_alt = np.random.exponential(
                player_params.loc[wr1_dropdown_alt, "mean"],
            )
            wr2_score_alt = np.random.exponential(
                player_params.loc[wr2_dropdown_alt, "mean"],
            )
            wr3_score_alt = np.random.exponential(
                player_params.loc[wr3_dropdown_alt, "mean"],
            )
            te_score_alt = np.random.exponential(
                player_params.loc[te_dropdown_alt, "mean"],
            )
            flex_score_alt = np.random.exponential(
                player_params.loc[flex_dropdown_alt, "mean"],
            )
            kicker_score_alt = np.random.exponential(
                player_params.loc[k_dropdown_alt, "mean"],
            )
            dst_score_alt = np.random.exponential(
                player_params.loc[dst_dropdown_alt, "mean"],
            )

            total_score_alt = (
                qb_score_alt
                + rb1_score_alt
                + rb2_score_alt
                + wr1_score_alt
                + wr2_score_alt
                + wr3_score_alt
                + te_score_alt
                + flex_score_alt
                + kicker_score_alt
                + dst_score_alt
            )

            score_dist_alt.append(total_score_alt)

        fig = go.Figure()
        fig.add_trace(
            go.Histogram(x=score_dist, opacity=0.5, name="Original", marker_color="red")
        )
        fig.add_vline(x=np.median(score_dist), line_dash="dash", line_color="red")

        fig.add_trace(
            go.Histogram(
                x=score_dist_alt, opacity=0.5, name="Alternative", marker_color="blue"
            )
        )
        fig.add_vline(x=np.median(score_dist_alt), line_dash="dash", line_color="blue")
        fig.update_layout(
            title_text="Sampled Results",  # title of plot
            xaxis_title_text="Team Points",  # xaxis label
            yaxis_title_text="Count",  # yaxis label
            bargap=0.2,  # gap between bars of adjacent location coordinates
            template="plotly_white",
        )

        return fig

    else:
        return go.Figure()


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
