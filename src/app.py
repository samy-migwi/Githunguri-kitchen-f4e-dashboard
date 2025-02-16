import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots

# Load your data
df = pd.read_csv(r"C:\Users\Qwon\Desktop\Clients\food4e\Term1\wrangle\dfw1w2w3.csv")
dmap = pd.read_csv(r"C:\Users\Qwon\Desktop\Clients\food4e\Term1\wrangle\map2.csv")

# Convert 'Date' column to datetime with the correct format
# df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, format='%d/%m/%y')  # Use '%y' for 2-digit year

# Generate the Folium map and save it as 'schools_map.html'
def generate_folium_map():
     # Define a color map for each Division
    division_colors = {
        'Githunguri  i': 'blue',
        'Githunguri  II': 'green',
        'Division3': 'red',
        'Cluster 12': 'purple',
    }

    # Calculate bounds for the big rectangle
    min_lat = dmap['lat'].min() - 0.01
    max_lat = dmap['lat'].max() + 0.01
    min_lon = dmap['lon'].min() - 0.01
    max_lon = dmap['lon'].max() + 0.01

    # Create a folium map centered around the average latitude and longitude
    center_lat = dmap['lat'].mean()
    center_lon = dmap['lon'].mean()
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        control_scale=True,
        zoom_control=True,
        scrollWheelZoom=True,
        dragging=True
    )

    # Add markers and rectangles
    for index, row in dmap.iterrows():
        color = division_colors.get(row['Division'], 'gray')  # Default to gray if Division not in color map
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=row['School'],
            tooltip=row['School'],
            icon=folium.Icon(color=color)
        ).add_to(m)

        # DivIcon for the school name
        folium.Marker(
            location=[row['lat'], row['lon']],
            icon=folium.DivIcon(html=f"""<div style="font-size: 12px; color: {color}; white-space: nowrap;">{row['School']}</div>""")
        ).add_to(m)

    # Add a smaller red box for the headquarters (Ikinu)
    hq = dmap[dmap['School'] == 'Ikinu Primary'].iloc[0]
    folium.Rectangle(
        bounds=[[hq['lat'] - 0.005, hq['lon'] - 0.005], [hq['lat'] + 0.005, hq['lon'] + 0.005]],
        color='red',
        fill=False
    ).add_to(m)

    # Add a big rectangle encompassing all the schools
    folium.Rectangle(
        bounds=[[min_lat, min_lon], [max_lat, max_lon]],
        color='red',
        fill=False,
        weight=2
    ).add_to(m)

    # Fit the map to the bounds of all markers
    m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

   
    # Add markers and other map features here
    m.save('schools_map.html')

# Generate the map file
generate_folium_map()

# Get unique dates and weeks from the DataFrame
available_dates = df['Date'].unique()
available_weeks = df['Week'].unique()

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server
app.title = "Githunguri Food4Education Dashboard"

# Define layout
app.layout = html.Div([
    html.H1("Githunguri Food4Education Dashboard", style={'textAlign': 'center', 'color': 'white', 'backgroundColor': '#2c3e50', 'padding': '20px'}),
    html.Div([
        dcc.Dropdown(
            id='date-dropdown',
            options=[{'label': date, 'value': date} for date in available_dates],
            value=available_dates[0],  # Default to the first available date
            clearable=False,
            style={'width': '50%', 'margin': '10px', 'backgroundColor': '#ecf0f1'}
        ),
        dcc.Dropdown(
            id='week-dropdown',
            options=[{'label': week, 'value': week} for week in available_weeks],
            value=available_weeks[0],  # Default to the first available week
            clearable=False,
            style={'width': '50%', 'margin': '10px', 'backgroundColor': '#ecf0f1'}
        )
    ], style={'textAlign': 'center', 'padding': '10px'}),
    html.Div([
        html.Div([
            dcc.Graph(id='projected-vs-actual', style={'height': '500px'})
        ], style={'width': '100%', 'display': 'inline-block', 'padding': '10px'}),
        html.Div([
            dcc.Graph(id='temperature-plot', style={'height': '500px'})
        ], style={'width': '40%', 'display': 'inline-block', 'padding': '10px'}),
        html.Div([
            dcc.Graph(id='top-bottom-schools', style={'height': '500px'})
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ]),
    html.Div([
        html.Div([
            dcc.Graph(id='kitchen-report-table', style={'height': '500px'})
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        html.Div([
            dcc.Graph(id='kitchen-report-sum', style={'height': '500px'})
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ]),
    html.Div([
        html.Div([
            dcc.Graph(id='weekday-sunburst', style={'height': '800px'})
        ], style={'flex': '48%', 'padding': '0px', 'margin': '0px'}),  # 50% width, no padding or margin
        html.Div([
            dcc.Graph(id='school-sunburst', style={'height': '800px'})
        ], style={'flex': '48%', 'padding': '0px', 'margin': '0px'})  # 50% width, no padding or margin
    ], style={'display': 'flex', 'padding': '0px', 'margin': '0px'}),  # No padding or margin in the parent
    html.Div([
        html.Iframe(id='map-plot', srcDoc=open('schools_map.html', 'r').read(), width='100%', height='600')
    ], style={'padding': '10px'})
], style={'backgroundColor': '#f4f6f7', 'fontFamily': 'Arial, sans-serif'})

 


@app.callback(
    [Output('projected-vs-actual', 'figure'),
     Output('temperature-plot', 'figure'),
     Output('top-bottom-schools', 'figure'),
     Output('kitchen-report-table', 'figure'),
     Output('kitchen-report-sum', 'figure'),
     Output('weekday-sunburst', 'figure'),
     Output('school-sunburst', 'figure')],
    [Input('date-dropdown', 'value'),
     Input('week-dropdown', 'value')]
)
def update_dashboard(selected_date, selected_week):
    if not selected_date or not selected_week:
        raise PreventUpdate

    # Filter data based on selected date and week
    filtered_df = df[df['Date'] == selected_date]
    k_df = df[df['Week'] == selected_week]
    filtered_df = filtered_df.sort_values(by='Projected_Kids')


    # Generate the existing plots
    projected_vs_actual_fig = go.Figure()
    projected_vs_actual_fig.add_trace(
        go.Bar(x=filtered_df["School"], y=filtered_df["Projected_Kids"], name='Projected Kids', marker_color='blue',
               text=filtered_df["Projected_Kids"], textposition='outside')
    )
    projected_vs_actual_fig.add_trace(
        go.Bar(x=filtered_df["School"], y=filtered_df["Actual_Meals_Served"], name='Actual_Meals_Served', marker_color='green',
               text=filtered_df["Actual_Meals_Served"], textposition='outside')
    )
    projected_vs_actual_fig.add_trace(
        go.Bar(x=filtered_df["School"], y=filtered_df["Failed_Taps"], name='Failed Taps', marker_color='orange',
               text=filtered_df["Failed_Taps"], textposition='outside')
    )
    projected_vs_actual_fig.update_layout(
        title=f"Projected vs Actual Meals Served on {selected_date}",
        xaxis_title="School",
        yaxis_title="Number of Kids",
        barmode='group',
        margin=dict(l=50, r=50, t=50, b=50)
    )
    # Replace with your logic
    temperature_fig = go.Figure()
    min_rice_temp = filtered_df["Rice_Temp"].min()
    max_rice_temp = filtered_df["Rice_Temp"].max()
    min_gwb_temp = filtered_df["B_W_G_Temperatures"].min()
    max_gwb_temp = filtered_df["B_W_G_Temperatures"].max()
    
    temperature_fig = px.box(
        filtered_df,
        y=["Rice_Temp", "B_W_G_Temperatures"],
        points="all",
        title=f"Temperature Distribution on {selected_date}",
        labels={"value": "Temperature (°c)", "variable": "Food Type"},
        color_discrete_sequence=["#1f77b4", "#ff7f0e"],
        hover_data={'School': True}
        
    )
    ## Add min and max annotations for Rice_temp1f77b4
    temperature_fig.add_annotation(
        x=0, y=min_rice_temp,
        text=f"Min Rice Temp: {min_rice_temp}°c",
        showarrow=True,
        arrowhead=1,
        ax=-40, ay=-40
    )
    temperature_fig.add_annotation(
        x=0, y=max_rice_temp,
        text=f"Max Rice Temp: {max_rice_temp}°c",
        showarrow=True,
        arrowhead=1,
        ax=-40, ay=40
    )
    # Add min and max annotations for G_W_B_temp
    temperature_fig.add_annotation(
        x=1, y=min_gwb_temp,
        text=f"Min G_W_B Temp: {min_gwb_temp}°c",
        showarrow=True,
        arrowhead=1,
        ax=40, ay=-40
    )

    temperature_fig.add_annotation(
        x=1, y=max_gwb_temp,
        text=f"Max G_W_B Temp: {max_gwb_temp}°",
        showarrow=True,
        arrowhead=1,
        ax=40, ay=40
    )
    
    temperature_fig.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="65°F")
    temperature_fig.update_layout(margin=dict(l=50, r=50, t=50, b=50))
    # Replace with your logic
    combined_fig = go.Figure()  # Replace with your logic
    # 3. Top and Bottom 5 Schools by Meals Served
    # Ensure "School" column is string and drop missing values
    filtered_df["School"] = filtered_df["School"].astype(str)
    filtered_df = filtered_df.dropna(subset=["School", "Actual_Meals_Served"])

    # Sort data for top 10 and bottom 10
    top_5 = filtered_df.nlargest(5, "Actual_Meals_Served")  # Top 10 schools
    bottom_5 = filtered_df.nsmallest(5, "Actual_Meals_Served")  # Bottom 10 schools

    # Sort top_10 in descending order and bottom_5 in ascending order for better contrast
    top_5 = top_5.sort_values(by="Actual_Meals_Served", ascending=True)
    bottom_5 = bottom_5.sort_values(by="Actual_Meals_Served", ascending=False)

    # Create subplots for better contrast
    combined_fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Top 10 Schools by Meals Served",
            "Bottom 10 Schools by Meals Served"
        )
    )

    # Plot top 10 schools (ascending bars for better contrast)
    # Plot top 10 schools (ascending bars for better contrast)
    # Plot top 10 schools (ascending bars for better contrast)
    combined_fig.add_trace(
        go.Bar(
            x=top_5["Actual_Meals_Served"],
            y=top_5["School"],
            orientation='h',
            marker=dict(color='green'),
            name="Top 10 Schools",
            text=top_5["Actual_Meals_Served"],  # Add values to the bars
            textposition="auto"  # Position the text automatically
        ),
        row=1, col=1
    )


# Plot bottom 10 schools (right-to-left orientation for better contrast)
    combined_fig.add_trace(
        go.Bar(
            x=bottom_5["Actual_Meals_Served"],
            y=bottom_5["School"],
            orientation='h',
            marker=dict(color='orange'),
            name="Bottom 10 Schools",
            text=bottom_5["Actual_Meals_Served"],  # Add values to the bars
            textposition="auto"  # Position the text automatically
        ),
        row=1, col=2
    )

    # Update x-axis for right-to-left orientation
    combined_fig.update_xaxes(
        range=[max(bottom_5["Actual_Meals_Served"]), 0],  # Reverse the range for right-to-left
        row=1, col=2
    )

    # Update layout
    combined_fig.update_layout(
        title_text="Top and Bottom 10 Schools by Meals Served",
        showlegend=False,
        #height=600,  # Adjust for dashboard harmony
        #width=1200,  # Adjust for dashboard harmony
        margin=dict(l=150, r=50, t=100, b=50)
    )

    # Update axes for better readability
    combined_fig.update_yaxes(tickfont=dict(size=10))
    combined_fig.update_xaxes(title="Actual Meals Served")
    # 4. Kitchen Report - Summary Table
    kitchen_table_fig = go.Figure(data=[go.Table(
        header=dict(values=["Metric", "Sum", "Mean", "Min", "Max", "Std Dev"],
                    fill_color='#2c3e50', font=dict(color='white'), align='left'),
        cells=dict(values=[
            ["Projected_Kids", "Successful_Taps", "Missed_Projection", "Rice_Received", "B_W_G_Received", "Rice_Remaining", "B_W_G_Remaining"],
            [filtered_df["Projected_Kids"].sum(), filtered_df["Successful_Taps"].sum(), filtered_df["Missed_Projection"].sum(),
             filtered_df["Rice_Received"].sum(), filtered_df["B_W_G_Received"].sum(), filtered_df["Rice_Remaining"].sum(), filtered_df["B_W_G_Remaining"].sum()],
            [filtered_df["Projected_Kids"].mean(), filtered_df["Successful_Taps"].mean(), filtered_df["Missed_Projection"].mean(),
             filtered_df["Rice_Received"].mean(), filtered_df["B_W_G_Received"].mean(), filtered_df["Rice_Remaining"].mean(), filtered_df["B_W_G_Remaining"].mean()],
            [filtered_df["Projected_Kids"].min(), filtered_df["Successful_Taps"].min(), filtered_df["Missed_Projection"].min(),
             filtered_df["Rice_Received"].min(), filtered_df["B_W_G_Received"].min(), filtered_df["Rice_Remaining"].min(), filtered_df["B_W_G_Remaining"].min()],
            [filtered_df["Projected_Kids"].max(), filtered_df["Successful_Taps"].max(), filtered_df["Missed_Projection"].max(),
             filtered_df["Rice_Received"].max(), filtered_df["B_W_G_Received"].max(), filtered_df["Rice_Remaining"].max(), filtered_df["B_W_G_Remaining"].max()],
            [filtered_df["Projected_Kids"].std(), filtered_df["Successful_Taps"].std(), filtered_df["Missed_Projection"].std(),
             filtered_df["Rice_Received"].std(), filtered_df["B_W_G_Received"].std(), filtered_df["Rice_Remaining"].std(), filtered_df["B_W_G_Remaining"].std()]
        ], fill_color='#ecf0f1', align='left')
    )])
    kitchen_table_fig.update_layout(
        title=f"Kitchen Report Summary for {selected_date}",
        margin=dict(l=50, r=50, t=50, b=50)
    )

    # 5. Kitchen Report - Sum Bar Chart
    kitchen_sum_fig = go.Figure()
    metrics = ["Projected_Kids", "Successful_Taps", "Missed_Projection", "Rice_Received", "B_W_G_Received", "Rice_Remaining", "B_W_G_Remaining"]
    sums = [filtered_df[metric].sum() for metric in metrics]
    kitchen_sum_fig.add_trace(go.Bar(x=metrics, y=sums, marker_color='blue', text=sums, textposition='outside'))
    kitchen_sum_fig.update_layout(
        title=f"Sum of Metrics for {selected_date}",
        xaxis_title="Metric",
        yaxis_title="Sum",
        margin=dict(l=50, r=50, t=50, b=50)
    )

    # Generate the new sunburst charts
    weekday_sunburst = px.sunburst(
        k_df, path=["Weekday", "School"], values="Actual_Meals_Served",
        color="Actual_Meals_Served", color_continuous_scale='RdBu',
        width=800, height=700, title=f"A PROJECTED MEALS FOR 2025 {selected_week} TERM 1"
    )
    weekday_sunburst.update_layout(
        paper_bgcolor='#ffffff ', plot_bgcolor='#111111', font=dict(color='#111111'))
    weekday_sunburst.update_traces(textinfo="label+value+percent entry")

    school_sunburst = px.sunburst(
        k_df, path=["School", "Weekday"], values="Actual_Meals_Served",
        color="Actual_Meals_Served", color_continuous_scale='RdBu',
        width=800, height=700, title="A PROJECTED MEALS FOR 2025 TERM 1"
    )
    school_sunburst.update_layout(
        paper_bgcolor='#ffffff', plot_bgcolor='#111111', font=dict(color='#111111'))
    school_sunburst.update_traces(textinfo="label+value+percent entry")

    return (projected_vs_actual_fig, temperature_fig, combined_fig, kitchen_table_fig,
            kitchen_sum_fig, weekday_sunburst, school_sunburst)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
   