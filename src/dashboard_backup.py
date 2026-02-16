import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, date
from dash.exceptions import PreventUpdate

# ─── App Initialization ───────────────────────────────────────────────────────
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Food for Education – Githunguri Kitchen Dashboard"

# ─── SAMPLE DATA (replace df = pd.read_csv(...) with your actual path) ───────
# Using realistic embedded sample data matching your notebook columns
SCHOOLS = [
    "Kahunira Primary", "Kahunira Secondary", "Ciiko Primary",
    "Githunguri Technical & Secondary", "Kiababu Primary", "Kiambururu Primary",
    "Gathangari Primary", "Gitiha Secondary", "Githioro Primary",
    "Gitombo Primary", "Githiga Primary", "Kiambururu Secondary",
    "Gikang'A Kageche Secondary", "Gatitu Primary", "Matuguta Secondary",
    "Mukuyu Secondary", "Ihiga Primary", "Gathaithi Primary",
    "Gathaithi Secondary", "Matuguta Primary", "Mathanja Primary",
    "Gataka Primary", "Kanyore Primary", "Gathiruini Primary",
    "Kindiga Primary", "Githima Primary", "Gatina Primary",
    "Kiawaiguru Primary", "Kiawairia Primary", "Kiawairia Secondary"
]

SCHOOL_TYPES = ["Primary" if "Primary" in s or "Comprehensive" in s else "Secondary" for s in SCHOOLS]
KITCHENS = ["Githunguri" if i < 22 else "kiambu kitchen" for i in range(len(SCHOOLS))]

DATES = ["1/5/2026","1/6/2026","1/7/2026","1/8/2026","1/9/2026",
         "1/12/2026","1/13/2026","1/14/2026","1/15/2026","1/16/2026",
         "1/19/2026","1/20/2026","1/21/2026","1/22/2026","1/23/2026",
         "1/26/2026","1/27/2026","1/28/2026","1/29/2026","1/30/2026"]

MENUS = ["Rice and Greengrams","Rice and Beans","Rice and Lentils","Rice and Greengrams",
         "Rice and Beans","Rice and Greengrams","Rice and Beans","Rice and Lentils",
         "Rice and Greengrams","Rice and Beans","Rice and Greengrams","Rice and Beans",
         "Rice and Lentils","Rice and Greengrams","Rice and Beans","Rice and Greengrams",
         "Rice and Beans","Rice and Lentils","Rice and Greengrams","Rice and Beans"]

np.random.seed(42)
rows = []
for d_idx, date_str in enumerate(DATES):
    for s_idx, school in enumerate(SCHOOLS):
        projected = np.random.randint(80, 800)
        actual = int(projected * np.random.uniform(0.88, 1.12))
        successful_taps = int(actual * np.random.uniform(0.88, 0.98))
        failed = actual - successful_taps
        f4e_kids = max(0, int(np.random.uniform(0, 30)))
        teachers = np.random.randint(0, 5)
        staff = np.random.randint(0, 3)
        new_reg = np.random.randint(0, 8)
        new_tags = np.random.randint(0, 12)
        lunch_min = np.random.randint(30, 75)
        next_day = projected + np.random.randint(-20, 30)
        rows.append({
            "Kitchen": KITCHENS[s_idx],
            "School": school,
            "School_Type": SCHOOL_TYPES[s_idx],
            "Date": date_str,
            "Menu": MENUS[d_idx],
            "Rice_variant": "White" if d_idx % 3 != 0 else "Brown",
            "Projected_Kids": projected,
            "Actual_Meals_Served": actual,
            "Successful_Taps": successful_taps,
            "F4E_Supported_Kids": f4e_kids,
            "Teachers": teachers,
            "Staff_Meals": staff,
            "Failed_Taps": failed,
            "New_Registrations": new_reg,
            "New_Tags_Replaced": new_tags,
            "Lunch_Time_Min": lunch_min,
            "Next_Day_Projection_Students": next_day,
        })

df=pd.read_csv("https://raw.githubusercontent.com/samy-migwi/Githunguri-kitchen-f4e-dashboard/main/data/df_upto_30_01_26.csv")

# ─── Date Options ─────────────────────────────────────────────────────────────
available_dates = sorted(df["Date"].unique(), key=lambda x: datetime.strptime(x, "%m/%d/%Y"))
date_options = [{"label": d, "value": d} for d in available_dates]

# ─── Colour Palette ───────────────────────────────────────────────────────────
C = {
    "bg":       "#0F1923",
    "panel":    "#162130",
    "card":     "#1C2B3A",
    "border":   "#243447",
    "teal":     "#00C9A7",
    "blue":     "#3B82F6",
    "amber":    "#F59E0B",
    "red":      "#EF4444",
    "green":    "#22C55E",
    "sky":      "#38BDF8",
    "text":     "#E2E8F0",
    "muted":    "#64748B",
    "white":    "#FFFFFF",
}

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'DM Sans', sans-serif", color=C["text"], size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        bgcolor="rgba(22,33,48,0.8)",
        bordercolor=C["border"],
        borderwidth=1,
        font=dict(color=C["text"], size=11),
    ),
    xaxis=dict(
        gridcolor=C["border"],
        linecolor=C["border"],
        tickcolor=C["border"],
        tickfont=dict(color=C["muted"], size=10),
        title_font=dict(color=C["muted"]),
    ),
    yaxis=dict(
        gridcolor=C["border"],
        linecolor=C["border"],
        tickcolor=C["border"],
        tickfont=dict(color=C["muted"], size=10),
        title_font=dict(color=C["muted"]),
    ),
)

# Layout for bar chart: white interior, dark labels for contrast
BAR_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FFFFFF",
    font=dict(family="'DM Sans', sans-serif", color="#111827", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#D1D5DB",
        borderwidth=1,
        font=dict(color="#111827", size=11),
    ),
    xaxis=dict(
        gridcolor="#E5E7EB",
        linecolor="#D1D5DB",
        tickcolor="#D1D5DB",
        tickfont=dict(color="#111827", size=10, family="'DM Sans', sans-serif"),
        title_font=dict(color="#374151"),
    ),
    yaxis=dict(
        gridcolor="#E5E7EB",
        linecolor="#D1D5DB",
        tickcolor="#D1D5DB",
        tickfont=dict(color="#374151", size=10),
        title_font=dict(color="#374151"),
    ),
)

# ─── KPI Card Helper ──────────────────────────────────────────────────────────
def kpi_card(card_id, icon, label, color):
    return html.Div([
        html.Div([
            html.Span(icon, style={"fontSize": "22px"}),
        ], style={
            "width": "44px", "height": "44px",
            "background": f"linear-gradient(135deg, {color}33, {color}15)",
            "border": f"1px solid {color}55",
            "borderRadius": "10px",
            "display": "flex", "alignItems": "center", "justifyContent": "center",
            "flexShrink": "0",
        }),
        html.Div([
            html.Div(label, style={"fontSize": "11px", "color": C["muted"], "fontWeight": "500",
                                   "textTransform": "uppercase", "letterSpacing": "0.08em",
                                   "marginBottom": "4px"}),
            html.Div(id=card_id, children="—",
                     style={"fontSize": "22px", "fontWeight": "700", "color": C["white"],
                            "lineHeight": "1"}),
        ]),
    ], style={
        "background": C["card"],
        "border": f"1px solid {C['border']}",
        "borderRadius": "12px",
        "padding": "16px 18px",
        "display": "flex",
        "alignItems": "center",
        "gap": "14px",
        "flex": "1",
        "minWidth": "160px",
        "transition": "border-color 0.2s",
    })

# ─── Layout ───────────────────────────────────────────────────────────────────
app.layout = html.Div([
    # Google Font import
    html.Link(rel="stylesheet",
              href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap"),

    # ── Sidebar ──────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Img(src="https://via.placeholder.com/36x36/00C9A7/FFFFFF?text=F4E",
                     style={"borderRadius": "8px", "width": "36px", "height": "36px"}),
            html.Div([
                html.Div("Food for Education", style={"fontWeight": "700", "fontSize": "13px",
                                                       "color": C["white"]}),
                html.Div("Githunguri Kitchen", style={"fontSize": "11px", "color": C["muted"]}),
            ]),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px",
                  "padding": "20px 18px 16px", "borderBottom": f"1px solid {C['border']}"}),

        html.Div([
            html.Div("📅  SELECT DATE", style={"fontSize": "10px", "fontWeight": "600",
                                               "color": C["muted"], "letterSpacing": "0.1em",
                                               "marginBottom": "8px", "paddingLeft": "4px"}),
            dcc.DatePickerSingle(
                id="date-picker",
                date=datetime.strptime(available_dates[-1], "%m/%d/%Y").strftime("%Y-%m-%d"),
                min_date_allowed=datetime.strptime(available_dates[0], "%m/%d/%Y"),
                max_date_allowed=datetime.strptime(available_dates[-1], "%m/%d/%Y"),
                display_format="D MMM YYYY",
                calendar_orientation="vertical",
                style={"width": "180px", "transform": "scale(0.82)", "transformOrigin": "top left"},
                className="dash-datepicker",
            ),
            # Show available dates as pills
            html.Div("Available dates:", style={"fontSize": "10px", "color": C["muted"],
                                                "marginTop": "16px", "marginBottom": "8px",
                                                "fontWeight": "600", "letterSpacing": "0.08em",
                                                "textTransform": "uppercase"}),
            html.Div([
                html.Div(
                    datetime.strptime(d, "%m/%d/%Y").strftime("%d %b"),
                    id={"type": "date-pill", "index": d},
                    n_clicks=0,
                    style={
                        "padding": "4px 8px",
                        "borderRadius": "6px",
                        "fontSize": "10px",
                        "cursor": "pointer",
                        "background": C["border"],
                        "color": C["muted"],
                        "fontWeight": "500",
                        "whiteSpace": "nowrap",
                    }
                ) for d in available_dates
            ], style={"display": "flex", "flexWrap": "wrap", "gap": "4px"}),

        ], style={"padding": "16px 12px"}),

        html.Div([
            html.Div("KITCHEN FILTER", style={"fontSize": "10px", "fontWeight": "600",
                                               "color": C["muted"], "letterSpacing": "0.1em",
                                               "marginBottom": "8px", "paddingLeft": "4px"}),
            dcc.Checklist(
                id="kitchen-filter",
                options=[
                    {"label": " Githunguri", "value": "Githunguri"},
                    {"label": " Kiambu Kitchen", "value": "kiambu kitchen"},
                ],
                value=["Githunguri", "kiambu kitchen"],
                labelStyle={"display": "block", "marginBottom": "8px",
                            "color": C["text"], "fontSize": "12px", "cursor": "pointer"},
                inputStyle={"marginRight": "8px", "accentColor": C["teal"]},
            ),
        ], style={"padding": "4px 12px 16px"}),

        html.Div([
            html.Div("SCHOOL TYPE", style={"fontSize": "10px", "fontWeight": "600",
                                            "color": C["muted"], "letterSpacing": "0.1em",
                                            "marginBottom": "8px", "paddingLeft": "4px"}),
            dcc.Checklist(
                id="school-type-filter",
                options=[
                    {"label": " Primary", "value": "Primary"},
                    {"label": " Secondary", "value": "Secondary"},
                ],
                value=["Primary", "Secondary"],
                labelStyle={"display": "block", "marginBottom": "8px",
                            "color": C["text"], "fontSize": "12px", "cursor": "pointer"},
                inputStyle={"marginRight": "8px", "accentColor": C["teal"]},
            ),
        ], style={"padding": "4px 12px 16px"}),

        html.Div([
            html.Div("🏫  SCHOOL VIEW", style={"fontSize": "10px", "fontWeight": "600",
                                               "color": C["muted"], "letterSpacing": "0.1em",
                                               "marginBottom": "8px", "paddingLeft": "4px"}),
            html.Div("Select a school to see its trend over time",
                     style={"fontSize": "10px", "color": C["muted"], "marginBottom": "8px",
                            "paddingLeft": "4px", "lineHeight": "1.4"}),
            dcc.Dropdown(
                id="school-dropdown",
                options=[{"label": s, "value": s} for s in sorted(df["School"].unique())],
                value=None,
                multi=False,
                placeholder="All schools (daily view)",
                clearable=True,
                style={"fontSize": "11px"},
                className="school-dropdown",
            ),
        ], style={"padding": "4px 12px 16px"}),

        html.Div([
            html.Div(id="selected-date-display", style={
                "background": f"linear-gradient(135deg, {C['teal']}22, {C['teal']}08)",
                "border": f"1px solid {C['teal']}44",
                "borderRadius": "10px",
                "padding": "12px",
                "textAlign": "center",
            }),
        ], style={"padding": "8px 12px", "marginTop": "auto"}),

    ], style={
        "width": "220px",
        "minWidth": "220px",
        "background": C["panel"],
        "borderRight": f"1px solid {C['border']}",
        "display": "flex",
        "flexDirection": "column",
        "height": "100vh",
        "overflowY": "auto",
        "position": "sticky",
        "top": "0",
    }),

    # ── Main Content ─────────────────────────────────────────────────────────
    html.Div([

        # Header bar
        html.Div([
            html.Div([
                html.Div("Daily Operations Report", style={
                    "fontSize": "20px", "fontWeight": "700",
                    "color": C["white"], "letterSpacing": "-0.3px"
                }),
                html.Div(id="header-subtitle", style={
                    "fontSize": "13px", "color": C["muted"], "marginTop": "2px"
                }),
            ]),
            html.Div([
                html.Div(id="menu-badge", style={
                    "background": f"linear-gradient(135deg, {C['teal']}33, {C['teal']}15)",
                    "border": f"1px solid {C['teal']}44",
                    "borderRadius": "20px",
                    "padding": "6px 14px",
                    "fontSize": "12px",
                    "color": C["teal"],
                    "fontWeight": "600",
                }),
            ]),
        ], style={
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "center", "padding": "20px 24px 16px",
            "borderBottom": f"1px solid {C['border']}",
            "background": C["panel"],
            "position": "sticky", "top": "0", "zIndex": "10",
        }),

        # ── KPI Row ──────────────────────────────────────────────────────────
        html.Div([
            kpi_card("kpi-projected",    "🎯", "Projected Kids",   C["blue"]),
            kpi_card("kpi-actual",       "🍽️", "Meals Served",     C["teal"]),
            kpi_card("kpi-failed",       "❌", "Failed Taps",      C["red"]),
            kpi_card("kpi-precision",    "📊", "Precision",        C["amber"]),
            kpi_card("kpi-teachers",     "👩‍🏫", "Teachers Fed",    C["sky"]),
            kpi_card("kpi-tags",         "🏷️", "Tags Replaced",    C["green"]),
            kpi_card("kpi-next-day",     "📅", "Next Day Proj.",   C["blue"]),
        ], style={
            "display": "flex", "flexWrap": "wrap", "gap": "12px",
            "padding": "20px 24px 0",
        }),

        # ── Kitchen breakdown ─────────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div("🏠", style={"fontSize": "16px"}),
                html.Div("Githunguri Kitchen", style={"fontSize": "12px", "color": C["muted"],
                                                       "marginBottom": "2px"}),
                html.Div(id="kitchen-githunguri", style={"fontSize": "18px",
                                                          "fontWeight": "700", "color": C["teal"]}),
            ], style={
                "background": C["card"], "border": f"1px solid {C['border']}",
                "borderRadius": "10px", "padding": "14px 18px", "flex": "1", "textAlign": "center",
            }),
            html.Div([
                html.Div("🏠", style={"fontSize": "16px"}),
                html.Div("Kiambu Kitchen", style={"fontSize": "12px", "color": C["muted"],
                                                   "marginBottom": "2px"}),
                html.Div(id="kitchen-kiambu", style={"fontSize": "18px",
                                                      "fontWeight": "700", "color": C["sky"]}),
            ], style={
                "background": C["card"], "border": f"1px solid {C['border']}",
                "borderRadius": "10px", "padding": "14px 18px", "flex": "1", "textAlign": "center",
            }),
        ], style={"display": "flex", "gap": "12px", "padding": "12px 24px 0"}),

        # ── Chart Row 1: Projected vs Actual + Pie ────────────────────────────
        html.Div([
            html.Div([
                html.Div(id="bar-chart-title",
                         style={"fontSize": "13px", "fontWeight": "600", "color": C["text"],
                                "marginBottom": "2px"}),
                html.Div(id="bar-chart-subtitle",
                         style={"fontSize": "11px", "color": C["muted"], "marginBottom": "8px"}),
                dcc.Graph(id="chart-bar-projected", config={"displayModeBar": False},
                          style={"height": "340px"}),
            ], style={
                "background": C["card"], "border": f"1px solid {C['border']}",
                "borderRadius": "12px", "padding": "16px", "flex": "2",
            }),

            html.Div([
                html.Div("Primary vs Secondary",
                         style={"fontSize": "13px", "fontWeight": "600", "color": C["text"],
                                "marginBottom": "4px"}),
                html.Div("Meals distribution by school type",
                         style={"fontSize": "11px", "color": C["muted"]}),
                dcc.Graph(id="chart-pie-type", config={"displayModeBar": False},
                          style={"height": "340px"}),
            ], style={
                "background": C["card"], "border": f"1px solid {C['border']}",
                "borderRadius": "12px", "padding": "16px", "flex": "1",
            }),
        ], style={"display": "flex", "gap": "12px", "padding": "12px 24px 0"}),

        # ── Chart Row 2: Precision deviation + Least failed taps ─────────────
        html.Div([
            html.Div([
                html.Div("Estimation Precision Deviation – Top 5 Schools",
                         style={"fontSize": "13px", "fontWeight": "600", "color": C["text"],
                                "marginBottom": "4px"}),
                html.Div("Closer to 0 = better projection accuracy",
                         style={"fontSize": "11px", "color": C["muted"]}),
                dcc.Graph(id="chart-precision", config={"displayModeBar": False},
                          style={"height": "300px"}),
            ], style={
                "background": C["card"], "border": f"1px solid {C['border']}",
                "borderRadius": "12px", "padding": "16px", "flex": "1",
            }),

            html.Div([
                html.Div("Top 5 Schools – Least Failed Taps",
                         style={"fontSize": "13px", "fontWeight": "600", "color": C["text"],
                                "marginBottom": "4px"}),
                html.Div("Schools with best tap compliance",
                         style={"fontSize": "11px", "color": C["muted"]}),
                dcc.Graph(id="chart-failed-taps", config={"displayModeBar": False},
                          style={"height": "300px"}),
            ], style={
                "background": C["card"], "border": f"1px solid {C['border']}",
                "borderRadius": "12px", "padding": "16px", "flex": "1",
            }),
        ], style={"display": "flex", "gap": "12px", "padding": "12px 24px 0"}),

        # ── Chart Row 3: Lunch time + Historical trend ─────────────────────
        html.Div([
            html.Div([
                html.Div("Lunch Duration by School (minutes)",
                         style={"fontSize": "13px", "fontWeight": "600", "color": C["text"],
                                "marginBottom": "4px"}),
                html.Div("Average time to complete lunch taping session",
                         style={"fontSize": "11px", "color": C["muted"]}),
                dcc.Graph(id="chart-lunch-time", config={"displayModeBar": False},
                          style={"height": "280px"}),
            ], style={
                "background": C["card"], "border": f"1px solid {C['border']}",
                "borderRadius": "12px", "padding": "16px", "flex": "1",
            }),

            html.Div([
                html.Div("Total Daily Meals – Historical Trend",
                         style={"fontSize": "13px", "fontWeight": "600", "color": C["text"],
                                "marginBottom": "4px"}),
                html.Div("Actual vs Projected across all available dates",
                         style={"fontSize": "11px", "color": C["muted"]}),
                dcc.Graph(id="chart-trend", config={"displayModeBar": False},
                          style={"height": "280px"}),
            ], style={
                "background": C["card"], "border": f"1px solid {C['border']}",
                "borderRadius": "12px", "padding": "16px", "flex": "2",
            }),
        ], style={"display": "flex", "gap": "12px", "padding": "12px 24px 20px"}),

    ], style={"flex": "1", "overflowY": "auto", "background": C["bg"]}),

], style={
    "display": "flex",
    "height": "100vh",
    "fontFamily": "'DM Sans', sans-serif",
    "background": C["bg"],
    "color": C["text"],
    "overflow": "hidden",
})


# ─── Callbacks ────────────────────────────────────────────────────────────────

def filter_df(date_str, kitchens, school_types):
    """Return filtered dataframe for the selected date."""
    fdf = df[
        (df["Date"] == date_str) &
        (df["Kitchen"].isin(kitchens)) &
        (df["School_Type"].isin(school_types))
    ]
    return fdf


@app.callback(
    Output("header-subtitle", "children"),
    Output("selected-date-display", "children"),
    Output("menu-badge", "children"),
    Output("kpi-projected", "children"),
    Output("kpi-actual", "children"),
    Output("kpi-failed", "children"),
    Output("kpi-precision", "children"),
    Output("kpi-teachers", "children"),
    Output("kpi-tags", "children"),
    Output("kpi-next-day", "children"),
    Output("kitchen-githunguri", "children"),
    Output("kitchen-kiambu", "children"),
    Output("bar-chart-title", "children"),
    Output("bar-chart-subtitle", "children"),
    Output("chart-bar-projected", "figure"),
    Output("chart-pie-type", "figure"),
    Output("chart-precision", "figure"),
    Output("chart-failed-taps", "figure"),
    Output("chart-lunch-time", "figure"),
    Output("chart-trend", "figure"),
    Input("date-picker", "date"),
    Input("kitchen-filter", "value"),
    Input("school-type-filter", "value"),
    Input("school-dropdown", "value"),
)
def update_all(selected_date, kitchens, school_types, selected_school):
    if not selected_date or not kitchens or not school_types:
        raise PreventUpdate

    # Convert date picker format (YYYY-MM-DD) → notebook format (M/D/YYYY)
    dt = datetime.strptime(selected_date, "%Y-%m-%d")
    date_str = dt.strftime("%-m/%-d/%Y")   # Linux: removes leading zeros

    fdf = filter_df(date_str, kitchens, school_types)

    if fdf.empty:
        empty_fig = go.Figure(layout={**PLOT_LAYOUT, "annotations": [{
            "text": "No data for selected date / filters",
            "xref": "paper", "yref": "paper", "x": 0.5, "y": 0.5,
            "showarrow": False, "font": {"size": 14, "color": C["muted"]},
        }]})
        no_data = "—"
        return (
            f"{dt.strftime('%A, %d %B %Y')} — No data",
            html.Div("No data", style={"color": C["muted"], "fontSize": "12px"}),
            "No data",
            no_data, no_data, no_data, no_data, no_data, no_data, no_data,
            no_data, no_data,
            "No data", "No data",
            empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig,
        )

    # ── KPIs ─────────────────────────────────────────────────────────────────
    total_projected = fdf["Projected_Kids"].sum()
    total_actual    = fdf["Actual_Meals_Served"].sum()
    total_failed    = fdf["Failed_Taps"].sum()
    precision       = total_actual / total_projected if total_projected else 0
    total_teachers  = fdf["Teachers"].sum()
    total_tags      = fdf["New_Tags_Replaced"].sum()
    total_next_day  = fdf["Next_Day_Projection_Students"].sum()

    menu        = fdf["Menu"].iloc[0] if len(fdf) else "—"
    rice_var    = fdf["Rice_variant"].iloc[0] if len(fdf) else ""

    # Per-kitchen meals
    kit_gb = fdf.groupby("Kitchen")["Actual_Meals_Served"].sum()
    g_meals = f"{kit_gb.get('Githunguri', 0):,}"
    k_meals = f"{kit_gb.get('kiambu kitchen', 0):,}"

    header_sub  = f"{dt.strftime('%A, %d %B %Y')} · {len(fdf)} schools reporting"
    menu_label  = f"🍚 {menu} · {rice_var} Rice"

    date_display = html.Div([
        html.Div(dt.strftime("%d"), style={"fontSize": "28px", "fontWeight": "800",
                                            "color": C["teal"], "lineHeight": "1"}),
        html.Div(dt.strftime("%b %Y"), style={"fontSize": "11px", "color": C["muted"],
                                              "marginTop": "2px"}),
        html.Div(dt.strftime("%A"), style={"fontSize": "10px", "color": C["muted"],
                                           "marginTop": "1px"}),
    ])

    # ── Chart 1: Projected vs Actual — school view or daily all-schools view ────
    if selected_school:
        # Single school selected → show trend over all dates (x = date)
        school_trend = df[
            (df["School"] == selected_school) &
            (df["Kitchen"].isin(kitchens)) &
            (df["School_Type"].isin(school_types))
        ].copy()
        school_trend["Date_parsed"] = pd.to_datetime(school_trend["Date"], format="%m/%d/%Y")
        school_trend = school_trend.sort_values("Date_parsed")

        bar_title = f"{selected_school} — Daily Trend"
        bar_subtitle = "Meals over time · white plot interior · selected date highlighted"

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="Projected", x=school_trend["Date"], y=school_trend["Projected_Kids"],
            marker_color=C["blue"], marker_line_width=0, opacity=0.85,
            text=school_trend["Projected_Kids"], textposition="outside",
            textfont=dict(size=9, color="#6B7280"),
        ))
        fig_bar.add_trace(go.Bar(
            name="Actual Meals", x=school_trend["Date"], y=school_trend["Actual_Meals_Served"],
            marker_color=C["teal"], marker_line_width=0,
            text=school_trend["Actual_Meals_Served"], textposition="outside",
            textfont=dict(size=9, color="#111827"),
        ))
        fig_bar.add_trace(go.Bar(
            name="Failed Taps", x=school_trend["Date"], y=school_trend["Failed_Taps"],
            marker_color=C["amber"], marker_line_width=0, opacity=0.85,
            text=school_trend["Failed_Taps"], textposition="outside",
            textfont=dict(size=9, color="#6B7280"),
        ))
        # Highlight the currently selected date
        if date_str in school_trend["Date"].values:
            row = school_trend[school_trend["Date"] == date_str]
            fig_bar.add_vline(
                x=date_str,
                line_dash="dot", line_color=C["amber"], line_width=2,
                annotation_text="Selected date",
                annotation_font_color=C["amber"],
                annotation_font_size=10,
            )
        fig_bar.update_layout(**BAR_LAYOUT,
            barmode="group",
            xaxis_tickangle=-40,
            bargap=0.2, bargroupgap=0.05,
            showlegend=True,
            yaxis_title="Count",
        )
    else:
        # No school selected → default daily all-schools bar chart
        bar_title = "Projected vs Actual Meals by School"
        bar_subtitle = f"All schools · {dt.strftime('%d %b %Y')} · white plot interior"

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="Projected", x=fdf["School"], y=fdf["Projected_Kids"],
            marker_color=C["blue"], marker_line_width=0, opacity=0.85,
            text=fdf["Projected_Kids"], textposition="outside",
            textfont=dict(size=9, color="#6B7280"),
        ))
        fig_bar.add_trace(go.Bar(
            name="Actual Meals", x=fdf["School"], y=fdf["Actual_Meals_Served"],
            marker_color=C["teal"], marker_line_width=0,
            text=fdf["Actual_Meals_Served"], textposition="outside",
            textfont=dict(size=9, color="#111827"),
        ))
        fig_bar.add_trace(go.Bar(
            name="Failed Taps", x=fdf["School"], y=fdf["Failed_Taps"],
            marker_color=C["amber"], marker_line_width=0, opacity=0.85,
            text=fdf["Failed_Taps"], textposition="outside",
            textfont=dict(size=9, color="#6B7280"),
        ))
        fig_bar.update_layout(**BAR_LAYOUT,
            barmode="group",
            xaxis_tickangle=-40,
            bargap=0.2, bargroupgap=0.05,
            showlegend=True,
            yaxis_title="Count",
        )

    # ── Chart 2: Pie – Primary vs Secondary ─────────────────────────────────
    type_gb = fdf.groupby("School_Type")["Actual_Meals_Served"].sum().reset_index()
    fig_pie = go.Figure(go.Pie(
        labels=type_gb["School_Type"],
        values=type_gb["Actual_Meals_Served"],
        marker=dict(colors=[C["blue"], C["teal"]],
                    line=dict(color=C["bg"], width=2)),
        textfont=dict(color=C["white"], size=12),
        hovertemplate="%{label}: %{value:,} meals<br>%{percent}<extra></extra>",
        hole=0.45,
    ))
    fig_pie.update_layout(**PLOT_LAYOUT, showlegend=True,
        annotations=[dict(text=f"{total_actual:,}", x=0.5, y=0.5, font_size=16,
                          font_color=C["white"], showarrow=False, font_family="DM Sans")])

    # ── Chart 3: Precision Deviation ─────────────────────────────────────────
    _prec_agg = fdf.groupby("School")[["Actual_Meals_Served", "Projected_Kids"]].sum()
    school_prec = (_prec_agg["Actual_Meals_Served"] / _prec_agg["Projected_Kids"] - 1).reset_index()
    school_prec.columns = ["School", "Deviation"]
    school_prec["AbsDev"] = school_prec["Deviation"].abs()
    top5 = school_prec.sort_values("AbsDev").head(5)
    bar_colors = [C["green"] if v >= 0 else C["red"] for v in top5["Deviation"]]

    fig_prec = go.Figure(go.Bar(
        x=top5["School"], y=top5["Deviation"],
        marker_color=bar_colors, marker_line_width=0,
        text=top5["Deviation"].round(3), textposition="outside",
        textfont=dict(size=10, color=C["text"]),
    ))
    fig_prec.add_hline(y=0, line_dash="dot", line_color=C["amber"], line_width=2)
    fig_prec.update_layout(**PLOT_LAYOUT,
        yaxis_title="Deviation (Actual/Proj − 1)",
        xaxis_tickangle=-15,
    )

    # ── Chart 4: Least Failed Taps ───────────────────────────────────────────
    school_ft = fdf.groupby("School")["Failed_Taps"].sum().reset_index()
    top5_ft   = school_ft.sort_values("Failed_Taps").head(5)
    ft_colors = [C["green"] if v == 0 else C["sky"] for v in top5_ft["Failed_Taps"]]

    fig_ft = go.Figure(go.Bar(
        x=top5_ft["School"], y=top5_ft["Failed_Taps"],
        marker_color=ft_colors, marker_line_width=0,
        text=top5_ft["Failed_Taps"], textposition="outside",
        textfont=dict(size=10, color=C["text"]),
    ))
    # Tick marks for zero-tap schools
    zero_schools = top5_ft[top5_ft["Failed_Taps"] == 0]["School"].tolist()
    for sch in zero_schools:
        fig_ft.add_annotation(
            x=sch, y=0, yshift=32, text="✓",
            showarrow=False,
            font=dict(color=C["green"], size=28, family="DM Sans"),
        )
    fig_ft.update_layout(**PLOT_LAYOUT,
        yaxis_title="Total Failed Taps",
        xaxis_tickangle=-15,
    )

    # ── Chart 5: Lunch Time ──────────────────────────────────────────────────
    lt_sorted = fdf.sort_values("Lunch_Time_Min", ascending=True)
    lt_colors_gradient = [
        C["teal"] if v <= 40 else (C["amber"] if v <= 55 else C["red"])
        for v in lt_sorted["Lunch_Time_Min"]
    ]
    fig_lt = go.Figure(go.Bar(
        x=lt_sorted["School"], y=lt_sorted["Lunch_Time_Min"],
        marker_color=lt_colors_gradient, marker_line_width=0,
        text=lt_sorted["Lunch_Time_Min"].astype(str) + "m",
        textposition="outside", textfont=dict(size=9, color=C["muted"]),
    ))
    fig_lt.add_hline(y=fdf["Lunch_Time_Min"].mean(), line_dash="dot",
                     line_color=C["blue"], line_width=1.5,
                     annotation_text=f"Avg: {fdf['Lunch_Time_Min'].mean():.0f}m",
                     annotation_font_color=C["blue"], annotation_font_size=10)
    fig_lt.update_layout(**PLOT_LAYOUT,
        yaxis_title="Minutes",
        xaxis_tickangle=-45,
    )

    # ── Chart 6: Historical Trend ─────────────────────────────────────────────
    trend = (
        df[(df["Kitchen"].isin(kitchens)) & (df["School_Type"].isin(school_types))]
        .groupby("Date")[["Projected_Kids", "Actual_Meals_Served"]]
        .sum()
        .reset_index()
    )
    trend["Date_parsed"] = pd.to_datetime(trend["Date"], format="%m/%d/%Y")
    trend = trend.sort_values("Date_parsed")

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend["Date"], y=trend["Projected_Kids"],
        name="Projected", mode="lines+markers",
        line=dict(color=C["blue"], width=2, dash="dot"),
        marker=dict(size=6, color=C["blue"]),
        fill=None,
    ))
    fig_trend.add_trace(go.Scatter(
        x=trend["Date"], y=trend["Actual_Meals_Served"],
        name="Actual", mode="lines+markers",
        line=dict(color=C["teal"], width=2.5),
        marker=dict(size=7, color=C["teal"]),
        fill="tonexty",
        fillcolor="rgba(0,201,167,0.09)",
    ))
    # Highlight selected date
    if date_str in trend["Date"].values:
        sel_actual = trend[trend["Date"] == date_str]["Actual_Meals_Served"].values[0]
        fig_trend.add_trace(go.Scatter(
            x=[date_str], y=[sel_actual],
            mode="markers", name="Selected",
            marker=dict(color=C["amber"], size=12, symbol="star",
                        line=dict(color=C["white"], width=1.5)),
        ))
    fig_trend.update_layout(**PLOT_LAYOUT,
        yaxis_title="Total Meals",
        xaxis_tickangle=-35,
        showlegend=True,
    )

    return (
        header_sub, date_display, menu_label,
        f"{total_projected:,}", f"{total_actual:,}", f"{total_failed:,}",
        f"{precision:.1%}", str(total_teachers), str(total_tags), f"{total_next_day:,}",
        g_meals, k_meals,
        bar_title, bar_subtitle,
        fig_bar, fig_pie, fig_prec, fig_ft, fig_lt, fig_trend,
    )


# ─── CSS overrides for dark date picker ───────────────────────────────────────
app.index_string = '''
<!DOCTYPE html>
<html>
<head>
{%metas%}
<title>{%title%}</title>
{%favicon%}
{%css%}
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0F1923; }
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: #0F1923; }
  ::-webkit-scrollbar-thumb { background: #243447; border-radius: 3px; }

  /* Date picker dark theme */
  .SingleDatePickerInput { background: #1C2B3A !important; border: 1px solid #243447 !important;
    border-radius: 8px !important; width: 100% !important; }
  .DateInput { background: transparent !important; width: 100% !important; }
  .DateInput_input { background: transparent !important; color: #E2E8F0 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 13px !important;
    font-weight: 600 !important; padding: 8px 10px !important; border: none !important;
    width: 100% !important; }
  .DateInput_input__focused { border-bottom: 2px solid #00C9A7 !important; }
  .SingleDatePicker_picker { background: #162130 !important; border: 1px solid #243447 !important;
    border-radius: 10px !important; z-index: 9999 !important; }
  .CalendarDay__default { background: #1C2B3A !important; color: #E2E8F0 !important;
    border: 1px solid #243447 !important; }
  .CalendarDay__default:hover { background: #243447 !important; color: #FFFFFF !important; }
  .CalendarDay__selected { background: #00C9A7 !important; color: #000 !important;
    border-color: #00C9A7 !important; }
  .CalendarDay__blocked_out_of_range { color: #64748B !important; }
  .CalendarMonthGrid { background: #162130 !important; }
  .CalendarMonth, .CalendarMonth_caption { background: #162130 !important;
    color: #E2E8F0 !important; }
  .DayPickerNavigation_button { background: #1C2B3A !important; border: 1px solid #243447 !important;
    border-radius: 6px !important; }
  .DayPickerNavigation_svg { fill: #E2E8F0 !important; }
  .DayPickerKeyboardShortcuts_show { display: none !important; }
  .DateRangePickerInput_clearDates, .SingleDatePickerInput_clearDate { display: none !important; }

  /* School dropdown dark theme — sidebar */
  .school-dropdown .Select-control { background: #1C2B3A !important; border: 1px solid #243447 !important; border-radius: 6px !important; }
  .school-dropdown .Select-menu-outer { background: #1C2B3A !important; border: 1px solid #243447 !important; border-radius: 6px !important; z-index: 9998 !important; }
  .school-dropdown .Select-option { background: #1C2B3A !important; color: #E2E8F0 !important; font-size: 11px !important; }
  .school-dropdown .Select-option:hover, .school-dropdown .Select-option.is-focused { background: #243447 !important; color: #FFFFFF !important; }
  .school-dropdown .Select-option.is-selected { background: #00C9A733 !important; color: #00C9A7 !important; }
  .school-dropdown .Select-single-value, .school-dropdown .Select-value-label { color: #00C9A7 !important; font-weight: 600 !important; font-size: 11px !important; }
  .school-dropdown .Select-placeholder { color: #64748B !important; font-size: 11px !important; }
  .school-dropdown .Select-input input { color: #E2E8F0 !important; font-size: 11px !important; }
  .school-dropdown .Select-arrow { border-top-color: #64748B !important; }
  .school-dropdown .Select-clear { color: #64748B !important; }
  .school-dropdown .Select-clear:hover { color: #EF4444 !important; }
</style>
</head>
<body>
{%app_entry%}
<footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>
'''

if __name__ == "__main__":
    print("🚀 Starting F4E Dashboard on http://127.0.0.1:8052")
    app.run(debug=True, host="0.0.0.0", port=8052)


df=pd.read_csv("https://raw.githubusercontent.com/samy-migwi/Githunguri-kitchen-f4e-dashboard/main/data/df_upto_30_01_26.csv")