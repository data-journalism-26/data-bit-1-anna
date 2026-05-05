import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import os

# --- Load data ---
base_path = os.path.dirname(__file__)
data_path = os.path.join(base_path, "..", "data", "Data.csv")

df = pd.read_csv(data_path)

# --- Clean columns ---
df.columns = df.columns.str.strip().str.lower()

df = df.rename(columns={
    "time_period": "year",
    "geo": "country",
    "gdp_pps": "gdp"
})

df["year"] = df["year"].astype(int)

# --- Variables ---
variables = {
    "HICP": "hicp",
    "Price Level Index": "pli",
    "GDP": "gdp",
    "Median Income": "median_income"
}

# --- App ---
app = Dash(__name__)

app.layout = html.Div([

    html.H1("Comparison of Economic Metrics in Europe"),

    html.P("""
    This interactive chart compares inflation (HICP), price levels (PLI),
    GDP, and median income across European countries.
    Select two years and countries to explore differences.
    """),

    html.Div([

        html.Label("X-axis"),
        dcc.Dropdown(
            options=[{"label": k, "value": v} for k, v in variables.items()],
            value="gdp",
            id="x-axis"
        ),

        html.Label("Y-axis"),
        dcc.Dropdown(
            options=[{"label": k, "value": v} for k, v in variables.items()],
            value="hicp",
            id="y-axis"
        ),

        html.Label("Select two years"),
        dcc.RangeSlider(
            min=df["year"].min(),
            max=df["year"].max(),
            step=1,
            value=[df["year"].min(), df["year"].max()],
            marks={int(y): str(y) for y in sorted(df["year"].unique())},
            id="year-range",
            allowCross=False
        ),

        html.Label("Select countries"),
        dcc.Dropdown(
            options=[{"label": c, "value": c} for c in sorted(df["country"].unique())],
            value=sorted(df["country"].unique()),
            multi=True,
            id="country-select"
        ),

    ], style={"width": "35%"}),

    dcc.Graph(id="scatter-plot")

])

# --- Callback ---
@app.callback(
    Output("scatter-plot", "figure"),
    Input("x-axis", "value"),
    Input("y-axis", "value"),
    Input("year-range", "value"),
    Input("country-select", "value")
)
def update_chart(x, y, year_range, selected_countries):

    year1, year2 = year_range

    dff = df[df["country"].isin(selected_countries)]

    dff1 = dff[dff["year"] == year1]
    dff2 = dff[dff["year"] == year2]

    # --- Plot ---
    fig = px.scatter(
        dff1,
        x=x,
        y=y,
        text="country",
        color_discrete_sequence=["blue"],
        hover_data={
            "country": True,
            "year": True,
            x: True,
            y: True
        }
    )

    # drugi rok jako druga warstwa
    fig2 = px.scatter(
        dff2,
        x=x,
        y=y,
        text="country",
        color_discrete_sequence=["red"],
        hover_data={
            "country": True,
            "year": True,
            x: True,
            y: True
        }
    )

    # dodaj trace’y
    for trace in fig2.data:
        trace.update(opacity=0.6, name=str(year2))
        fig.add_trace(trace)

    # podpisy
    fig.update_traces(textposition="top center")

    # legenda i layout
    fig.data[0].name = str(year1)

    fig.update_layout(
        title=f"{x.upper()} vs {y.upper()} ({year1} vs {year2})",
        xaxis_title=x.upper(),
        yaxis_title=y.upper(),
        legend_title="Year"
    )

    return fig


if __name__ == "__main__":
    app.run(debug=True)