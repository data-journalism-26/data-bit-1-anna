import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import os

# --- Load data ---
base_path = os.path.dirname(os.path.abspath(__file__))
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

SECTION = {
    "padding": "20px 32px",
    "maxWidth": "1400px",
    "margin": "0 auto",
    "fontFamily": "Georgia, serif",
    "color": "#1a1a1a"
}

CARD = {
    "background": "#f7f9fc",
    "border": "1px solid #dde3ed",
    "borderRadius": "8px",
    "padding": "16px 20px",
    "flex": "1",
    "minWidth": "200px"
}

app.layout = html.Div([

    # ── HEADER ────────────────────────────────────────────────────────────────
    html.Div([
        html.H1("Is Europe Converging? Comparing Living Standards Across the Continent",
                style={"fontSize": "28px", "marginBottom": "12px", "fontWeight": "bold"}),

        html.P([
            "Comparing living standards across countries is one of the most deceptively difficult tasks in economics. "
            "A salary of €2,000 per month means something very different in Bucharest than it does in Copenhagen. "
            "Raw numbers — wages, prices, GDP — rarely tell the full story on their own. To understand whether people "
            "in one country are truly better or worse off than those in another, you need to look at multiple dimensions "
            "at once: how much things cost, how much people earn, how fast prices are rising, and how productive the "
            "overall economy is. Even then, the picture keeps shifting — a country that looked affordable a decade ago "
            "may have caught up considerably, or fallen further behind.",
        ], style={"lineHeight": "1.75", "marginBottom": "12px", "fontSize": "15px"}),

        html.P([
            "This tool brings together four key economic indicators from Eurostat for European countries spanning "
            "nearly a decade. It lets you place any two metrics on a scatter plot, compare two different years "
            "side by side, and filter to the countries you care about. The goal is simple: to make it easier to "
            "see patterns, spot outliers, and ask better questions about how European economies relate to one another — "
            "and how they are changing over time."
        ], style={"lineHeight": "1.75", "marginBottom": "0", "fontSize": "15px"}),

    ], style=SECTION),

    # ── VARIABLE DESCRIPTIONS ─────────────────────────────────────────────────
    html.Div([
        html.H2("About the indicators", style={"fontSize": "18px", "marginBottom": "16px", "fontWeight": "bold"}),
        html.Div([

            html.Div([
                html.H3("Price Level Index (PLI)", style={"fontSize": "14px", "marginBottom": "6px", "color": "#1a6fdb"}),
                html.P(
                    "The PLI measures how expensive a country is relative to the EU27 average, which is set to 100. "
                    "A value of 130 means prices are 30% higher than the EU average; a value of 70 means 30% cheaper. "
                    "It is calculated by Eurostat using a basket of comparable goods and services across all member states, "
                    "making it one of the most reliable tools for cross-country price comparisons.",
                    style={"fontSize": "13px", "lineHeight": "1.6", "margin": 0}
                )
            ], style=CARD),

            html.Div([
                html.H3("GDP per Capita (PPS)", style={"fontSize": "14px", "marginBottom": "6px", "color": "#1a6fdb"}),
                html.P(
                    "GDP per capita expressed in Purchasing Power Standards (PPS) adjusts each country's economic output "
                    "for differences in price levels, allowing meaningful comparisons of prosperity. The EU27 average equals 100. "
                    "A country with a GDP PPS of 150 produces 50% more economic value per person than the average European, "
                    "in real terms. This removes the distortion caused by comparing nominal figures across economies "
                    "with very different cost structures.",
                    style={"fontSize": "13px", "lineHeight": "1.6", "margin": 0}
                )
            ], style=CARD),

            html.Div([
                html.H3("Median Income (PPS)", style={"fontSize": "14px", "marginBottom": "6px", "color": "#1a6fdb"}),
                html.P(
                    "Median equivalised net income represents the income of the middle person in a country's income "
                    "distribution — half earn more, half earn less. It is expressed in PPS euros, meaning it has already "
                    "been adjusted for purchasing power, so figures are directly comparable across countries. "
                    "Unlike average income, the median is not distorted by very high earners at the top, making it "
                    "a better reflection of what a typical household actually takes home.",
                    style={"fontSize": "13px", "lineHeight": "1.6", "margin": 0}
                )
            ], style=CARD),

            html.Div([
                html.H3("HICP Inflation (%)", style={"fontSize": "14px", "marginBottom": "6px", "color": "#1a6fdb"}),
                html.P(
                    "The Harmonised Index of Consumer Prices (HICP) is the standard measure of inflation used across "
                    "the EU, designed to be comparable between member states. It tracks the annual percentage change "
                    "in the prices of a harmonised basket of consumer goods and services. Because the methodology is "
                    "standardised across all countries, HICP allows you to compare how quickly prices rose — or fell — "
                    "in different economies in the same year, and is the basis for the ECB's inflation target of 2%.",
                    style={"fontSize": "13px", "lineHeight": "1.6", "margin": 0}
                )
            ], style=CARD),

        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),
    ], style=SECTION),

    # ── GŁÓWNY KONTENER – controls po lewej, wykres w środku, kraje po prawej
    html.Div([

        # Lewa kolumna – osie i suwak lat
        html.Div([

            html.Label("X-axis"),
            dcc.Dropdown(
                options=[{"label": k, "value": v} for k, v in variables.items()],
                value="gdp",
                id="x-axis"
            ),

            html.Label("Y-axis", style={"marginTop": "16px"}),
            dcc.Dropdown(
                options=[{"label": k, "value": v} for k, v in variables.items()],
                value="hicp",
                id="y-axis"
            ),

            html.Label("Select two years", style={"marginTop": "16px"}),
            dcc.RangeSlider(
                min=df["year"].min(),
                max=df["year"].max(),
                step=1,
                value=[df["year"].min(), df["year"].max()],
                marks={int(y): str(y) for y in sorted(df["year"].unique())},
                id="year-range",
                allowCross=False
            ),

        ], style={"width": "20%", "padding": "16px", "boxSizing": "border-box"}),

        # Środek – wykres
        html.Div([
            dcc.Graph(id="scatter-plot", style={"height": "600px"})
        ], style={"width": "55%"}),

        # Prawa kolumna – wybór krajów
        html.Div([
            html.Label("Select countries", style={"fontWeight": "bold", "marginBottom": "8px", "display": "block"}),
            dcc.Dropdown(
                options=[{"label": c, "value": c} for c in sorted(df["country"].unique())],
                value=sorted(df["country"].unique()),
                multi=True,
                id="country-select",
                style={"width": "100%"},
                optionHeight=35,
            ),
        ], style={
            "width": "23%",
            "padding": "16px",
            "boxSizing": "border-box",
        }),

    ], style={"display": "flex", "flexDirection": "row", "alignItems": "flex-start", "maxWidth": "1400px", "margin": "0 auto", "padding": "0 32px"}),

    # SOURCE
    html.Div([
        html.P([
            "Data source: ",
            html.A("Eurostat", href="https://ec.europa.eu/eurostat", target="_blank",
                   style={"color": "#1a6fdb"}),
            " — datasets: prc_ppp_ind (PLI), nama_10_pc (GDP PPS), ilc_di03 (Median Income), prc_hicp_aind (HICP). "
            "All figures refer to annual data. GDP and PLI are indexed to EU27 = 100."
        ], style={"fontSize": "12px", "color": "#666", "margin": 0})
    ], style={"padding": "8px 32px", "borderTop": "1px solid #dde3ed"}),

    # KEY FINDINGS
    html.Div([
        html.H2("What the data reveals", style={"fontSize": "18px", "marginBottom": "16px", "fontWeight": "bold"}),
        html.Div([
            html.Div([
                html.H3("The East–West price gap is narrowing", style={"fontSize": "14px", "marginBottom": "6px"}),
                html.P(
                    "A decade ago, countries like Bulgaria, Romania and Poland had price levels around 50% below the EU average. "
                    "That gap has been closing steadily. Compare PLI across years to see how Eastern European economies "
                    "have been converging toward Western price levels — even as wage convergence has lagged behind.",
                    style={"fontSize": "13px", "lineHeight": "1.6", "margin": 0}
                )
            ], style={"background": "#f7f9fc", "border": "1px solid #dde3ed", "borderRadius": "8px", "padding": "16px 20px", "flex": "1", "minWidth": "200px"}),

            html.Div([
                html.H3("When GDP lies: the Irish anomaly", style={"fontSize": "14px", "marginBottom": "6px"}),
                html.P(
                    "Try plotting GDP against Median Income and look for Ireland. Its GDP per capita (PPS) is among the "
                    "highest in Europe — but its median income tells a more modest story. This is the 'leprechaun economics' "
                    "effect: multinational companies book profits in Ireland, inflating GDP far beyond what Irish households "
                    "actually earn. It's a reminder that GDP alone can be a poor proxy for living standards.",
                    style={"fontSize": "13px", "lineHeight": "1.6", "margin": 0}
                )
            ], style={"background": "#f7f9fc", "border": "1px solid #dde3ed", "borderRadius": "8px", "padding": "16px 20px", "flex": "1", "minWidth": "200px"}),

            html.Div([
                html.H3("The 2022 inflation shock hit unevenly", style={"fontSize": "14px", "marginBottom": "6px"}),
                html.P(
                    "Set the year range to 2021–2023 and plot HICP against PLI. The Baltic states — Estonia, Latvia and "
                    "Lithuania — experienced some of the highest inflation rates in the EU, exceeding 15–20% at the peak. "
                    "Meanwhile, countries like France and Switzerland remained comparatively stable. "
                    "The energy crisis hit import-dependent, less-diversified economies hardest.",
                    style={"fontSize": "13px", "lineHeight": "1.6", "margin": 0}
                )
            ], style={"background": "#f7f9fc", "border": "1px solid #dde3ed", "borderRadius": "8px", "padding": "16px 20px", "flex": "1", "minWidth": "200px"}),

            html.Div([
                html.H3("Luxembourg: the continent's perennial outlier", style={"fontSize": "14px", "marginBottom": "6px"}),
                html.P(
                    "Luxembourg consistently appears as an extreme outlier in almost every combination of metrics. "
                    "It has the highest GDP per capita, among the highest price levels, and the highest median incomes "
                    "in Europe by a wide margin. Try filtering it out to see how the rest of Europe clusters.",
                    style={"fontSize": "13px", "lineHeight": "1.6", "margin": 0}
                )
            ], style={"background": "#f7f9fc", "border": "1px solid #dde3ed", "borderRadius": "8px", "padding": "16px 20px", "flex": "1", "minWidth": "200px"}),

        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),
    ], style={"padding": "20px 32px", "fontFamily": "Georgia, serif"}),

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

    # Starszy rok – czerwony, półprzezroczysty
    fig = px.scatter(
        dff1,
        x=x,
        y=y,
        text="country",
        color_discrete_sequence=["red"],
        hover_data={"country": True, "year": True, x: True, y: True}
    )
    for trace in fig.data:
        trace.update(
            opacity=0.45,
            name=str(year1),
            marker=dict(size=9)
        )

    # Nowszy rok – niebieski, wyraźny, na wierzchu
    fig2 = px.scatter(
        dff2,
        x=x,
        y=y,
        text="country",
        color_discrete_sequence=["#1a6fdb"],
        hover_data={"country": True, "year": True, x: True, y: True}
    )
    for trace in fig2.data:
        trace.update(
            opacity=1,
            name=str(year2),
            marker=dict(size=11, line=dict(width=1.5, color="white"))
        )
        fig.add_trace(trace)

    fig.update_traces(textposition="top center")

    fig.update_layout(
        title=f"{x.upper()} vs {y.upper()} ({year1} vs {year2})",
        xaxis_title=x.upper(),
        yaxis_title=y.upper(),
        legend_title="Year"
    )

    return fig


server = app.server 

if __name__ == "__main__":
    app.run(debug=False)