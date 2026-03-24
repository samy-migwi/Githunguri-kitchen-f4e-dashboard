import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, date
from dash.exceptions import PreventUpdate
import folium
from folium.plugins import MarkerCluster, MiniMap

# ─── App Initialization ───────────────────────────────────────────────────────
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Food for Education – Githunguri Kitchen Dashboard"

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
#df = pd.read_csv("gs://f4e_data_processed_csv/df_upto_feb_24_26.csv") #remote 

#local db with mounted folder 
#df=pd.read_csv(r"C:\Users\Administrator\Desktop\ds\f4e\githunguri1\Githunguri-kitchen-f4e-dashboard\data\data_processed\mar_03_26_clean.csv")
#df=pd.read_csv()
#df = pd.read_csv(r"C:\\Users\\Administrator\\Desktop\\ds\\f4e\\githunguri1\\Githunguri-kitchen-f4e-dashboard\\data\\data_processed\\mar_03_26_clean.csv")
df=pd.read_csv("/opt/airflow/data/data_processed/df_upto_mar_03_26.csv")


#https://github.com/samy-migwi/Githunguri-kitchen-f4e-dashboard/blob/d1999890d4027d30536320f4c45fb49916d1f317/data/data_processed/df_upto_feb_24_26.csv
dmap = pd.read_csv("gs://f4e_data_processed_csv/map2.csv")

# Clean column names in dmap (remove spaces and standardize)
dmap.columns = dmap.columns.str.strip().str.replace(' ', '_').str.replace('__', '_')

# ─── Date Options ─────────────────────────────────────────────────────────────
def _parse_date(d):
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%-m/%-d/%Y"):
        try:
            return datetime.strptime(d, fmt)
        except ValueError:
            pass
    return datetime.min

available_dates = sorted(df["Date"].unique(), key=_parse_date)
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
    "map_text": "#00C9A7",  # Green color for map school names
}

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
# Load data
dmap = pd.read_csv("https://raw.githubusercontent.com/samy-migwi/Githunguri-kitchen-f4e-dashboard/main/data/map2.csv")
dmap.columns = dmap.columns.str.strip().str.replace(' ', '_').str.replace('__', '_')

def generate_folium_map(selected_school=None):
    # Color map for divisions
    division_colors = {
        'Githunguri i': '#2563EB',      # Blue
        'Githunguri II': '#16A34A',     # Green  
        'Githunguri I': '#2563EB',      # Blue
        'Cluster 12': '#9333EA',        # Purple
    }
    
    # Clean division data
    dmap['Division'] = dmap['Division'].str.strip()
    
    # Calculate bounds
    min_lat = dmap['lat'].min() - 0.02
    max_lat = dmap['lat'].max() + 0.02
    min_lon = dmap['lon'].min() - 0.02
    max_lon = dmap['lon'].max() + 0.02
    
    center_lat = dmap['lat'].mean()
    center_lon = dmap['lon'].mean()
    
    # Create map with NATURAL terrain as default
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', # Natural terrain view
        control_scale=True,
        #attr='© OpenStreetMap contributors'
    )
    
    # Add alternative tile layers
    folium.TileLayer(
        'CartoDB positron',
        name='Clean Light',
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        'CartoDB dark_matter',
        name='Dark Mode',
        control=True
    ).add_to(m)
    
    # Add satellite option
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        control=True
    ).add_to(m)
    
    # Column names
    school_col = 'School'
    lat_col = 'lat'
    lon_col = 'lon'
    division_col = 'Division'
    f4e_col = 'F4E_Sponsored' if 'F4E_Sponsored' in dmap.columns else 'F4E__Sponsored' if 'F4E__Sponsored' in dmap.columns else None
    pop_col = 'Total_Population' if 'Total_Population' in dmap.columns else None
    incharge_col = 'Tsm_Incharge' if 'Tsm_Incharge' in dmap.columns else 'Tsm__Incharge' if 'Tsm__Incharge' in dmap.columns else None
    
    # Add markers for each school
    for idx, row in dmap.iterrows():
        is_selected = selected_school and selected_school in str(row[school_col])
        base_color = division_colors.get(row[division_col], '#4B5563')
        
        # Selected school gets red highlight
        marker_color = '#DC2626' if is_selected else base_color
        
        # Create popup content
        popup_html = f"""
        <div style="font-family: system-ui, sans-serif; min-width: 200px;">
            <h4 style="margin: 0 0 8px 0; color: {marker_color}; 
                       border-bottom: 2px solid {marker_color}; padding-bottom: 6px;
                       font-size: 13px; font-weight: 600;">
                {row[school_col]}{' ⭐ SELECTED' if is_selected else ''}
            </h4>
            <p style="margin: 4px 0; font-size: 11px;"><strong>Division:</strong> {row[division_col]}</p>
        """
        
        if f4e_col and pd.notna(row.get(f4e_col)) and row.get(f4e_col) != 0:
            popup_html += f'<p style="margin: 4px 0; font-size: 11px;"><strong>F4E Sponsored:</strong> <span style="color: #059669; font-weight: 600;">{int(row[f4e_col])}</span></p>'
        
        if pop_col and pd.notna(row.get(pop_col)) and row.get(pop_col) != 0:
            popup_html += f'<p style="margin: 4px 0; font-size: 11px;"><strong>Total Population:</strong> {int(row[pop_col])}</p>'
        
        if incharge_col and pd.notna(row.get(incharge_col)) and str(row.get(incharge_col)).strip():
            popup_html += f'<p style="margin: 4px 0; font-size: 11px;"><strong>Incharge:</strong> {row[incharge_col]}</p>'
        
        popup_html += "</div>"
        
        # Create circle marker
        folium.CircleMarker(
            location=[row[lat_col], row[lon_col]],
            radius=9 if is_selected else 7,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=folium.Tooltip(row[school_col], permanent=False),
            color=marker_color,
            fill=True,
            fillColor=marker_color,
            fillOpacity=0.9 if is_selected else 0.7,
            weight=4 if is_selected else 2,
        ).add_to(m)
        
        # Add school name label with white background for natural map visibility
        # Stagger labels vertically to reduce overlap
        offset_y = 15 if idx % 2 == 0 else -5
        
        folium.Marker(
            location=[row[lat_col], row[lon_col]],
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    font-size: 10px;
                    color: {'#DC2626' if is_selected else '#1F2937'};
                    font-weight: {'800' if is_selected else '700'};
                    white-space: nowrap;
                    font-family: system-ui, sans-serif;
                    background: rgba(255,255,255,0.95);
                    padding: 2px 6px;
                    border-radius: 4px;
                    border: 2px solid {marker_color};
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    transform: translate(-50%, {offset_y}px);
                    display: inline-block;
                    pointer-events: none;
                ">
                    {row[school_col]}{' ★' if is_selected else ''}
                </div>
                """,
                icon_size=(180, 30),
                icon_anchor=(90, 15),
            ),
            interactive=False
        ).add_to(m)
    
    # Add coverage area rectangle
    folium.Rectangle(
        bounds=[[min_lat, min_lon], [max_lat, max_lon]],
        color='#DC2626',
        fill=True,
        fillColor='#DC2626',
        fillOpacity=0.05,
        weight=2,
        dash_array='5, 8',
        popup='Kitchen Coverage Area'
    ).add_to(m)
    
    # Add Ikinu HQ
    hq_data = dmap[dmap[school_col].str.contains('Ikinu', case=False, na=False)]
    if not hq_data.empty:
        hq = hq_data.iloc[0]
        
        # HQ boundary
        folium.Rectangle(
            bounds=[
                [hq[lat_col] - 0.007, hq[lon_col] - 0.007], 
                [hq[lat_col] + 0.007, hq[lon_col] + 0.007]
            ],
            color='#B91C1C',
            fill=True,
            fillColor='#B91C1C',
            fillOpacity=0.1,
            weight=2,
            popup='HQ: Ikinu Primary'
        ).add_to(m)
        
        # HQ marker
        folium.Marker(
            location=[hq[lat_col], hq[lon_col]],
            popup='<b style="color: #B91C1C;">★ HQ: Ikinu Primary</b>',
            icon=folium.DivIcon(
                html="""
                <div style="
                    font-size: 24px; 
                    color: #B91C1C; 
                    text-shadow: 0 0 4px white, 0 0 8px white;
                    font-weight: bold;
                ">★</div>
                """,
                icon_size=(40, 40),
                icon_anchor=(20, 20),
            )
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl(position='topright', collapsed=True).add_to(m)
    
    # Add minimap
    MiniMap(
        tile_layer='OpenStreetMap',
        position='bottomright',
        width=140,
        height=140,
        zoom_level_offset=-5
    ).add_to(m)
    
    # Fit bounds with padding
    m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]], padding=[30, 30])
    
    return m



def get_map_html(selected_school=None):
    """Generate map and return as HTML string"""
    m = generate_folium_map(selected_school)
    return m._repr_html_()


# ─── Startup Diagnostics ──────────────────────────────────────────────────────
print(f"✅ Loaded {len(df)} rows | Date range: {available_dates[0]} → {available_dates[-1]}")
print(f"   Kitchens  : {sorted(df['Kitchen'].dropna().unique().tolist())}")
print(f"   SchoolType: {sorted(df['School_Type'].dropna().unique().tolist())}")
print(f"   Date sample: {df['Date'].iloc[0]!r}  (detected format: {'YYYY-MM-DD' if '-' in str(df['Date'].iloc[0]) else 'M/D/YYYY'})")


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
                date=_parse_date(available_dates[-1]).strftime("%Y-%m-%d"),
                min_date_allowed=_parse_date(available_dates[0]),
                max_date_allowed=_parse_date(available_dates[-1]),
                display_format="D MMM YYYY",
                calendar_orientation="vertical",
                style={"width": "180px", "transform": "scale(0.82)", "transformOrigin": "top left"},
                className="dash-datepicker",
            ),

        ], style={"padding": "16px 12px"}),

        html.Div([
            html.Div("CLUSTER FILTER", style={"fontSize": "10px", "fontWeight": "600",
                                               "color": C["muted"], "letterSpacing": "0.1em",
                                               "marginBottom": "8px", "paddingLeft": "4px"}),
            dcc.Checklist(
                id="cluster-filter",
                options=[{"label": f" {c}", "value": c} for c in sorted(df["Cluster"].dropna().unique())],
                value=list(df["Cluster"].dropna().unique()),
                labelStyle={"display": "block", "marginBottom": "8px",
                            "color": C["text"], "fontSize": "12px", "cursor": "pointer"},
                inputStyle={"marginRight": "8px", "accentColor": C["teal"]},
            ),
        ], style={"padding": "4px 12px 16px"}),

        html.Div([
            html.Div("KITCHEN FILTER", style={"fontSize": "10px", "fontWeight": "600",
                                               "color": C["muted"], "letterSpacing": "0.1em",
                                               "marginBottom": "8px", "paddingLeft": "4px"}),
            dcc.Checklist(
                id="kitchen-filter",
                options=[{"label": f" {k}", "value": k} for k in sorted(df["Kitchen"].dropna().unique())],
                value=list(df["Kitchen"].dropna().unique()),
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
                options=[{"label": f" {t}", "value": t} for t in sorted(df["School_Type"].dropna().unique())],
                value=list(df["School_Type"].dropna().unique()),
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
                "borderRadius": "12px", "padding": "16px", "flex": "3",  # Increased from 2 to 3
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
                "borderRadius": "12px", "padding": "16px", "flex": "1",  # Kept at 1
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
        ], style={"display": "flex", "gap": "12px", "padding": "12px 24px 0"}),

        # ── Map Section (MOVED TO LAST) ─────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div("🗺️ School Locations Map", 
                         style={"fontSize": "13px", "fontWeight": "600", "color": C["text"],
                                "marginBottom": "4px"}),
                html.Div("Interactive map showing all schools by division with F4E coverage (Green names = schools, Red = Selected)",
                         style={"fontSize": "11px", "color": C["muted"]}),
            ], style={"padding": "16px 16px 0"}),
            html.Iframe(
                id="folium-map",
                srcDoc=get_map_html(),
                style={
                    "width": "100%",
                    "height": "600px",
                    "border": "none",
                    "borderRadius": "0 0 12px 12px",
                }
            ),
        ], style={
            "background": C["card"], 
            "border": f"1px solid {C['border']}",
            "borderRadius": "12px", 
            "margin": "12px 24px 20px",
            "overflow": "hidden",
        }),

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

def filter_df(date_str, kitchens, school_types, clusters=None):
    """Return filtered dataframe for the selected date."""
    mask = (
        (df["Date"] == date_str) &
        (df["Kitchen"].isin(kitchens)) &
        (df["School_Type"].isin(school_types)) &
        (df["Cluster"].isin(clusters))
    )
    if clusters:
        mask &= df["Cluster"].isin(clusters)
    return df[mask]


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
    Output("folium-map", "srcDoc"),  # Added map output
    Input("date-picker", "date"),
    Input("kitchen-filter", "value"),
    Input("school-type-filter", "value"),
    Input("school-dropdown", "value"),
    Input("cluster-filter", "value"),
)
def update_all(selected_date, kitchens, school_types, selected_school, clusters):
    if not selected_date or not kitchens or not school_types or not clusters:
        raise PreventUpdate

    # Date picker gives YYYY-MM-DD; detect data format and match accordingly
    dt = datetime.strptime(selected_date, "%Y-%m-%d")
    # Auto-detect date format in data
    _sample = df["Date"].dropna().iloc[0] if not df["Date"].dropna().empty else ""
    if "-" in str(_sample) and str(_sample).index("-") == 4:
        # Data uses YYYY-MM-DD format
        date_str = selected_date  # e.g. "2026-01-05"
    else:
        # Data uses M/D/YYYY format (old format)
        date_str = f"{dt.month}/{dt.day}/{dt.year}"

    fdf = filter_df(date_str, kitchens, school_types, clusters)

    # Generate map with selected school highlighted
    map_html = get_map_html(selected_school)

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
            map_html,
        )

    # ── KPIs ─────────────────────────────────────────────────────────────────
    # If school selected, show only that school's data for the selected date
    if selected_school:
        school_data = fdf[fdf["School"] == selected_school]
        if not school_data.empty:
            total_projected = school_data["Projected_Kids"].sum()
            total_actual    = school_data["Actual_Meals_Served"].sum()
            total_failed    = school_data["Failed_Taps"].sum()
            precision       = total_actual / total_projected if total_projected else 0
            total_teachers  = school_data["Teachers"].sum()
            total_tags      = school_data["New_Tags_Replaced"].sum()
            total_next_day  = school_data["Next_Day_Projection_Students"].sum()
            menu            = school_data["Menu"].iloc[0]
            rice_var        = school_data["Rice_variant"].iloc[0]
        else:
            # Fallback to totals if no data for this school on this date
            total_projected = fdf["Projected_Kids"].sum()
            total_actual    = fdf["Actual_Meals_Served"].sum()
            total_failed    = fdf["Failed_Taps"].sum()
            precision       = total_actual / total_projected if total_projected else 0
            total_teachers  = fdf["Teachers"].sum()
            total_tags      = fdf["New_Tags_Replaced"].sum()
            total_next_day  = fdf["Next_Day_Projection_Students"].sum()
            menu            = fdf["Menu"].iloc[0] if len(fdf) else "—"
            rice_var        = fdf["Rice_variant"].iloc[0] if len(fdf) else ""
    else:
        total_projected = fdf["Projected_Kids"].sum()
        total_actual    = fdf["Actual_Meals_Served"].sum()
        total_failed    = fdf["Failed_Taps"].sum()
        precision       = total_actual / total_projected if total_projected else 0
        total_teachers  = fdf["Teachers"].sum()
        total_tags      = fdf["New_Tags_Replaced"].sum()
        total_next_day  = fdf["Next_Day_Projection_Students"].sum()
        menu            = fdf["Menu"].iloc[0] if len(fdf) else "—"
        rice_var        = fdf["Rice_variant"].iloc[0] if len(fdf) else ""

    # Per-kitchen meals
    kit_gb = fdf.groupby("Kitchen")["Actual_Meals_Served"].sum()
    all_kitchens = sorted(df["Kitchen"].dropna().unique())
    g_meals = f"{kit_gb.get(all_kitchens[0], 0):,}" if len(all_kitchens) > 0 else "—"
    k_meals = f"{kit_gb.get(all_kitchens[1], 0):,}" if len(all_kitchens) > 1 else "—"

    header_sub  = f"{dt.strftime('%A, %d %B %Y')} · {len(fdf)} schools reporting"
    if selected_school:
        header_sub += f" | Showing: {selected_school}"
    menu_label  = f"🍚 {menu} · {rice_var} Rice"

    date_display = html.Div([
        html.Div(dt.strftime("%d"), style={"fontSize": "28px", "fontWeight": "800",
                                            "color": C["teal"], "lineHeight": "1"}),
        html.Div(dt.strftime("%b %Y"), style={"fontSize": "11px", "color": C["muted"],
                                              "marginTop": "2px"}),
        html.Div(dt.strftime("%A"), style={"fontSize": "10px", "color": C["muted"],
                                           "marginTop": "1px"}),
    ])

    # ── Chart 1: Projected vs Actual ────
        # ── Chart 1: Projected vs Actual ────
    if selected_school:
        # Single school selected → show trend over all dates (x = date)
        school_trend = df[
            (df["School"] == selected_school) &
            (df["Kitchen"].isin(kitchens)) &
            (df["School_Type"].isin(school_types)) &
        (df["Cluster"].isin(clusters))
        ].copy()
        school_trend["Date_parsed"] = pd.to_datetime(school_trend["Date"], infer_datetime_format=True)
        school_trend = school_trend.sort_values("Date_parsed")

        bar_title = f"{selected_school} — Daily Trend"
        bar_subtitle = "Meals over time · selected date highlighted"

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="Projected", x=school_trend["Date_parsed"], y=school_trend["Projected_Kids"],
            marker_color=C["blue"], marker_line_width=0, opacity=0.85,
            text=school_trend["Projected_Kids"], textposition="outside",
            textfont=dict(size=9, color="#FFFFFF"),
        ))
        fig_bar.add_trace(go.Bar(
            name="Actual Meals", x=school_trend["Date_parsed"], y=school_trend["Actual_Meals_Served"],
            marker_color=C["teal"], marker_line_width=0,
            text=school_trend["Actual_Meals_Served"], textposition="outside",
            textfont=dict(size=9, color="#FFFFFF"),
        ))
        fig_bar.add_trace(go.Bar(
            name="Failed Taps", x=school_trend["Date_parsed"], y=school_trend["Failed_Taps"],
            marker_color=C["amber"], marker_line_width=0, opacity=0.85,
            text=school_trend["Failed_Taps"], textposition="outside",
            textfont=dict(size=9, color="#FFFFFF"),
        ))

        # Highlight selected date
        sel_dt = pd.to_datetime(date_str, infer_datetime_format=True)
        if sel_dt in school_trend["Date_parsed"].values:
            sel_actual = school_trend.loc[school_trend["Date_parsed"] == sel_dt, "Actual_Meals_Served"]
            if not sel_actual.empty:
                fig_bar.add_shape(
                    type="rect",
                    x0=sel_dt - pd.Timedelta(hours=12), x1=sel_dt + pd.Timedelta(hours=12),
                    y0=0, y1=school_trend["Actual_Meals_Served"].max() * 1.1,
                    fillcolor=C["red"], opacity=0.12, line_width=0,
                )
                fig_bar.add_annotation(
                    x=sel_dt, y=school_trend["Actual_Meals_Served"].max() * 1.15,
                    text="Selected", showarrow=False,
                    font=dict(color=C["red"], size=11),
                )
            
        fig_bar.update_layout(**{k: v for k, v in BAR_LAYOUT.items() if k != 'xaxis'},
            barmode="group",
            bargap=0.2, bargroupgap=0.05,
            showlegend=True,
            yaxis_title="Count",
            xaxis=dict(
                tickformat="%d %b",
                tickangle=-40,
                tickfont=dict(color="#111827", size=10),
                dtick="D1",
            ),
        )
    else:
        # No school selected → default daily all-schools bar chart
        bar_title = "Projected vs Actual Meals by School"
        bar_subtitle = f"All schools · {dt.strftime('%d %b %Y')} · sorted by actual meals"
        
        # Sort by Actual_Meals_Served in ascending order
        fdf_sorted = fdf.sort_values("Actual_Meals_Served", ascending=True)
        bar_title = "Projected vs Actual Meals by School"
        bar_subtitle = f"All schools · {dt.strftime('%d %b %Y')}"

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="Projected", x=fdf_sorted["School"], y=fdf_sorted["Projected_Kids"],
            marker_color="blue", marker_line_width=0, opacity=0.85,
            text=fdf_sorted["Projected_Kids"], textposition="outside",
            textfont=dict(size=9, color="#111827"), 
        ))
        fig_bar.add_trace(go.Bar(
            name="Actual Meals", x=fdf_sorted["School"], y=fdf_sorted["Actual_Meals_Served"],
            marker_color="green", marker_line_width=0,
            text=fdf_sorted["Actual_Meals_Served"], textposition="outside",
            textfont=dict(size=9, color="#111827"), 
        ))
        fig_bar.add_trace(go.Bar(
            name="Failed Taps",
            x=fdf_sorted["School"],
            y=fdf_sorted["Failed_Taps"],
            marker_color="orange",
            marker_line_width=0,
            opacity=0.85,
            text=fdf_sorted["Failed_Taps"],
            textposition="outside",
            textfont=dict(size=9, color="#111827"), 
        ))
        fig_bar.update_layout(**{k: v for k, v in BAR_LAYOUT.items() if k not in ['xaxis','margin','legend']},
            barmode="group",
            xaxis_tickangle=-40,
            bargap=0.2, bargroupgap=0.05,
            showlegend=True,
            yaxis_title="Count",
                legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#D1D5DB",
                borderwidth=1,
                font=dict(size=10, color="#111827"),
            ),
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(
                tickfont=dict(color="#FFFFFF", size=10),  # White x-axis labels
            ),
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
        hole=0.4,
        textinfo='label+percent',  # Show labels and percentages on the pie
        insidetextorientation='radial',  # Orient text radially inside
    ))
    fig_pie.update_layout(**{k: v for k, v in BAR_LAYOUT.items() if k != 'margin'}, 
        showlegend=False,  # Hide legend since labels are inside
        annotations=[dict(text=f"{total_actual:,}", x=0.5, y=0.5, font_size=14,
                          font_color=C["white"], showarrow=False, font_family="DM Sans")],
        margin=dict(l=10, r=10, t=30, b=10),  # Reduced margins
    )
   

    # ── Chart 3: Precision Deviation ─────────────────────────────────────────
    if selected_school:
        # Show only selected school's precision over time
        school_prec_data = df[
            (df["School"] == selected_school) &
            (df["Kitchen"].isin(kitchens)) &
            (df["School_Type"].isin(school_types)) &
        (df["Cluster"].isin(clusters))
        ].copy()
        school_prec_data["Precision"] = school_prec_data["Actual_Meals_Served"] / school_prec_data["Projected_Kids"]
        school_prec_data = school_prec_data.sort_values("Date")
        
        fig_prec = go.Figure(go.Scatter(
            x=school_prec_data["Date"],
            y=school_prec_data["Precision"],
            mode="lines+markers",
            marker=dict(color=C["teal"], size=8),
            line=dict(color=C["teal"], width=2),
            name="Precision"
        ))
        fig_prec.add_hline(y=1.0, line_dash="dash", line_color=C["amber"], line_width=2, 
                          annotation_text="Target (100%)", annotation_font_color=C["amber"])
        fig_prec.update_layout(**{k: v for k, v in BAR_LAYOUT.items() if k != 'yaxis'},
            yaxis_title="Precision (Actual/Projected)",
            xaxis_tickangle=-40,
            yaxis=dict(tickformat=".1%"),
        )
    else:
        # Show top 5 schools precision deviation
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

    # ── Chart 4: Failed Taps ───────────────────────────────────────────
    if selected_school:
        # Show selected school's failed taps over time
        school_failed_data = df[
            (df["School"] == selected_school) &
            (df["Kitchen"].isin(kitchens)) &
            (df["School_Type"].isin(school_types)) &
        (df["Cluster"].isin(clusters))
        ].copy()
        school_failed_data = school_failed_data.sort_values("Date")
        
        fig_ft = go.Figure(go.Bar(
            x=school_failed_data["Date"],
            y=school_failed_data["Failed_Taps"],
            marker_color=C["red"],
            text=school_failed_data["Failed_Taps"],
            textposition="outside",
        ))
        fig_ft.update_layout(**PLOT_LAYOUT,
            yaxis_title="Failed Taps",
            xaxis_tickangle=-40,
        )
    else:
        # Show top 5 schools with least failed taps
        school_ft = fdf.groupby("School")["Failed_Taps"].sum().reset_index()
        top5_ft   = school_ft.sort_values("Failed_Taps").head(5)
        ft_colors = [C["green"] if v == 0 else C["sky"] for v in top5_ft["Failed_Taps"]]

        fig_ft = go.Figure(go.Bar(
            x=top5_ft["School"], y=top5_ft["Failed_Taps"],
            marker_color=ft_colors, marker_line_width=0,
            text=top5_ft["Failed_Taps"], textposition="outside",
            textfont=dict(size=10, color=C["text"]),
        ))
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
    if selected_school:
        # Show selected school's lunch duration over time
        school_lunch_data = df[
            (df["School"] == selected_school) &
            (df["Kitchen"].isin(kitchens)) &
            (df["School_Type"].isin(school_types)) &
        (df["Cluster"].isin(clusters))
        ].copy()
        school_lunch_data = school_lunch_data.sort_values("Date")
        
        colors = [C["teal"] if v <= 40 else (C["amber"] if v <= 55 else C["red"]) 
                  for v in school_lunch_data["Lunch_Time_Min"]]
        
        fig_lt = go.Figure(go.Bar(
            x=school_lunch_data["Date"],
            y=school_lunch_data["Lunch_Time_Min"],
            marker_color=colors,
            text=school_lunch_data["Lunch_Time_Min"].astype(str) + "m",
            textposition="outside",
        ))
        avg_time = school_lunch_data["Lunch_Time_Min"].mean()
        fig_lt.add_hline(y=avg_time, line_dash="dot",
                        line_color=C["blue"], line_width=1.5,
                        annotation_text=f"Avg: {avg_time:.0f}m",
                        annotation_font_color=C["blue"])
        fig_lt.update_layout(**PLOT_LAYOUT,
            yaxis_title="Minutes",
            xaxis_tickangle=-40,
        )
    else:
        # Show all schools lunch duration for selected date
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
    if selected_school:
        # Show selected school's historical trend
        trend = df[
            (df["School"] == selected_school) &
            (df["Kitchen"].isin(kitchens)) &
            (df["School_Type"].isin(school_types)) &
        (df["Cluster"].isin(clusters))
        ].copy()
        trend["Date_parsed"] = pd.to_datetime(trend["Date"], infer_datetime_format=True)
        trend = trend.sort_values("Date_parsed")
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend["Date_parsed"], y=trend["Projected_Kids"],
            name="Projected", mode="lines+markers",
            line=dict(color=C["blue"], width=2, dash="dot"),
            marker=dict(size=6, color=C["blue"]),
        ))
        fig_trend.add_trace(go.Scatter(
            x=trend["Date_parsed"], y=trend["Actual_Meals_Served"],
            name="Actual", mode="lines+markers",
            line=dict(color=C["teal"], width=2.5),
            marker=dict(size=7, color=C["teal"]),
            fill="tonexty",
            fillcolor="rgba(0,201,167,0.09)",
        ))
        # Highlight selected date
        sel_date_parsed = pd.to_datetime(date_str, infer_datetime_format=True)
        if sel_date_parsed in trend["Date_parsed"].values:
            sel_row = trend[trend["Date_parsed"] == sel_date_parsed]
            if not sel_row.empty:
                sel_actual = sel_row["Actual_Meals_Served"].values[0]
                fig_trend.add_trace(go.Scatter(
                    x=[sel_date_parsed], y=[sel_actual],
                    mode="markers", name="Selected Date",
                    marker=dict(color=C["red"], size=14, symbol="star",
                               line=dict(color=C["white"], width=2)),
                ))
        fig_trend.update_layout(**PLOT_LAYOUT,
            yaxis_title="Meals",
            xaxis_title="Date",
            xaxis_tickformat="%d %b",
            showlegend=True,
        )
    else:
        # Show aggregate trend for all schools
        trend = (
            df[
                (df["Kitchen"].isin(kitchens)) &
                (df["School_Type"].isin(school_types)) &
                (df["Cluster"].isin(clusters))
            ]
            .groupby("Date")[["Projected_Kids", "Actual_Meals_Served"]]
            .sum()
            .reset_index()
        )
        trend["Date_parsed"] = pd.to_datetime(trend["Date"], infer_datetime_format=True)
        trend = trend.sort_values("Date_parsed")

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend["Date_parsed"], y=trend["Projected_Kids"],
            name="Projected", mode="lines+markers",
            line=dict(color=C["blue"], width=2, dash="dot"),
            marker=dict(size=6, color=C["blue"]),
            fill=None,
        ))
        fig_trend.add_trace(go.Scatter(
            x=trend["Date_parsed"], y=trend["Actual_Meals_Served"],
            name="Actual", mode="lines+markers",
            line=dict(color=C["teal"], width=2.5),
            marker=dict(size=7, color=C["teal"]),
            fill="tonexty",
            fillcolor="rgba(0,201,167,0.09)",
        ))
        # Highlight selected date
        sel_date_parsed = pd.to_datetime(date_str, infer_datetime_format=True)
        if sel_date_parsed in trend["Date_parsed"].values:
            sel_actual = trend[trend["Date_parsed"] == sel_date_parsed]["Actual_Meals_Served"].values[0]
            fig_trend.add_trace(go.Scatter(
                x=[sel_date_parsed], y=[sel_actual],
                mode="markers", name="Selected Date",
                marker=dict(color=C["amber"], size=12, symbol="star",
                           line=dict(color=C["white"], width=1.5)),
            ))
        fig_trend.update_layout(**PLOT_LAYOUT,
            yaxis_title="Total Meals",
            xaxis_title="Date",
            xaxis_tickformat="%d %b",
            showlegend=True,
        )

    return (
        header_sub, date_display, menu_label,
        f"{total_projected:,}", f"{total_actual:,}", f"{total_failed:,}",
        f"{precision:.1%}", str(total_teachers), str(total_tags), f"{total_next_day:,}",
        g_meals, k_meals,
        bar_title, bar_subtitle,
        fig_bar, fig_pie, fig_prec, fig_ft, fig_lt, fig_trend,
        map_html,
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
  
  /* Folium map iframe styling */
  iframe {
    border: none;
    background: white;
  }
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