import dash
from dash import dcc, html, Input, Output, State, dash_table, ALL, ctx
import pandas as pd
import re
from datetime import datetime

# Initialize the app
app = dash.Dash(__name__)

# List of schools to track
SCHOOLS_LIST = [
    "Kagema Primary School", "Mitahato Primary School", "Giathieko Primary School", 
    "Nyaga Primary School", "Githioro Primary School", "Kindiga Primary & Junior Secondary School", 
    "Ndireti Secondary School", "Kihuririo Primary School", "Miguta Primary School", 
    "Gathugu Secondary School", "Gitiha Secondary School", "Kigumo Secondary School", 
    "Kiawairia Primary", "Mukuyu Secondary School", "PCEA Matuguta Secondary School", 
    "Kiambururu Secondary School", "Gathangari Primary School", "Kibichoi Primary School", 
    "Miiri Secondary School", "Miguta Secondary School", "Kanyore Primary School", 
    "Miiri Primary", "Gathaithi Secondary School", "William Ng'iru Secondary School", 
    "Ihiga Primary", "Kambui Primary School", "Ndireti Primary School", 
    "Gatitu Primary", "Thuita Secondary School", "Ceb Riamute Nursery, Primary & Junior Secondary", 
    "Kanjai Secondary School", "PCEA Matuguta Primary & Junior Secondary School", "Kigumo Primary", 
    "Gitombo Primary School", "Ikinu Primary", "PCEA Mitahato Secondary School", 
    "Kagema Secondary School", "Githiga Primary", "Githima Primary", 
    "GATHAITHI PRIMARY", "Thuita Primary School", "Njunu Primary School", 
    "Kanjai Primary", "Nyaga Secondary School", "Kiawairia Secondary School", 
    "Ngewa Primary School", "Kiambururu Comprehensive School", "Gathugu Primary School", 
    "Komothai Primary School", "Gathiruini Primary School", "Catholic Archdiocese Of Nairobi Gataka Primary", 
    "Kiawaiguru Primary School", "Mathanja Priamry School", "Gatina Primary School", 
    "Gikang'a Kageche Secondary School", "Kibathi Comprehensive School", "Kiababu Primary School", 
    "Njenga Karume Comprehensive School", "St. Augustine Gatono Primary", "St. Joseph Gathanga Secondary School", 
    "Cianda Secondary School", "Kawaida Secondary School", "Gathanji Comprehensive School", 
    "Kiairia Comprehensive School", "St. Vincent Lioki Secondary School", "Riara Secondary School", 
    "Ndumberi Primary", "P.C.E.A Ngemwa Secondary School", "P.C.E.A Karia Secondary School", 
    "Kamondo Primary and Junior School", "ACK Riabai Primary School", "Kiambaa Comprehensive School", 
    "Benson Njau Primary School", "Ciiko Primary", "Mungai Chengecha Primary School", 
    "PCEA Githunguri Comprehensive School", "St. Joseph Riabai Secondary School", "Gicoco Primary School", 
    "Lioki Comprehensive School", "Maciri Primary School", "Gathanji Secondary School", 
    "Riara Primary School", "St. Peters Ndumberi Secondary School", "PCEA Karia Comprehensive School", 
    "Mukua Secondary School", "Kiairia Secondary School", "AK Magugu Comprehensive School", 
    "Ting'ang'a Model School", "Ting'ang'a Secondary School", "Kamondo Secondary School", 
    "Loreto Primary School", "Kahunira Secondary School", "HGM Ting'ang'a Secondary School", 
    "Kahunira Comprehensive School", "Gatatha Comprehensive School", "Ngemwa Primary and Junior School", 
    "HGM Ting'ang'a Primary School", "Chief Wandie Primary School", "Kawaida Comprehensive School", 
    "Kibubuti Primary School", "Githunguri Technical & Secondary School"
]

# Helper function to normalize school names for matching
def normalize_school_name(name):
    """Normalize school name for fuzzy matching while preserving original structure"""
    if not name:
        return ""
    # Just strip whitespace and convert to lowercase for matching
    # Don't remove any parts of the name
    return name.strip().lower()

# Helper function to extract data
def extract_data(raw_text):
    # Define patterns for extraction
    data_pattern = {
        # Kitchen - Fixed pattern to capture kitchen name properly
        "Kitchen": r"Kitchen\s*[:\-]\s*([^\n]+?)(?=\s*(?:School|SCHOOL|$))",
        "School": r"School\s*?:\s*?(.*?)(?=\s*Menu\s*:)",
        "Date": r"Date\s*?:\s*?([\d\-/]+)",
        "Menu": r"Menu\s*?:\s*?(.*?)(?=\s*Date\s*:)",
        "Projected_Kids": r"Projected\s+no\s+of\s+kids\s*?:\s*?(\d+)",
        "Actual_Meals_Served": r"Actual\s+meals\s+served\s*?:\s*?(\d+)",
        "Successful_Taps": r"Successful\s+Taps\s*?:\s*?(\d+)",
        
        # F4E variations - handles multiple formats
        "F4E_Supported_Kids": r"(?:F4E\s+Supported\s+Kids|F4E\s*/School/Sponsored\s+Others)\s*?:\s*?([\d+\(\)]+)",
        
        "Teachers": r"Teachers\s*?:\s*?(\d+)",
        "Staff_Meals": r"Staff\s+meals\s*?:\s*?(\d+)",
        "Failed_Taps": r"Failed\s+taps\s*?:\s*?(\d+)",
        "New_Registrations": r"New\s+registration(?:s)?\s*?:\s*?(\d+)",
        "New_Tags_Replaced": r"New\s+tags\s+replaced\s*?:\s*?(\d+)",

        # Food remaining section - handles both formats
        "Rice_Remaining": r"(?:Food\s+[Rr]emaining.*?)?Rice\s*?:\s*?(\d+\.?\d*)\s*[Kk]gs?",
        "B_W_G_Remaining": r"(?:Food\s+[Rr]emaining.*?)?(?:Beans|GreenGrams|Green grams|Western|G\.G|Wairimu|Stew)\s*?:\s*?(\d+\.?\d*)\s*[Kk]gs?",
                          
        # Other Information
        "Missed_Food": r"(?:No\s+of\s+kids\s+missed\s+food|No\.\s+of\s+kids\s+who\s+missed\s+food)\s*[:=]\s*?(\d+)",
        
        # Next day projection - handles both student-only and detailed format
        "Next_Day_Projection_Students": r"Next\s+Day'?s\s+Projection\s*?:.*?Students\s*?:\s*?(\d+)",
        "Next_Day_Projection_Teachers": r"Next\s+Day'?s\s+Projection\s*?:.*?Teachers\s*?:\s*?(\d+)",
        "Next_Day_Projection_Staff": r"Next\s+Day'?s\s+Projection\s*?:.*?Staff\s*?:\s*?(\d+)",
        
        # Tapping time - handles both old and new formats
        "Start_Taping": r"(?:Started\s+tapping\s+at|Started\s+at)\s*:?\s*(\d{1,2}\s+\w+\s+\d{4},\s+\d{2}:\d{2}:\d{2}|\d{1,2}:?\d{2}\s?(?:[apAP][mM]|hrs|HRS|Hrs)?)",
        "Stop_Taping": r"(?:to|To)\s*:?\s*(\d{1,2}\s+\w+\s+\d{4},\s+\d{2}:\d{2}:\d{2}|\d{1,2}:?\d{2}\s?(?:[apAP][mM]|hrs|HRS|Hrs)?)",

        # Comments
        "Projection_Comment": r"Comment\s+on\s+[Pp]rojection\s*?:\s*?(.*?)(?=\n|Report|$)",
        "Comment_1": r"Comment\s+1\s*?:\s*?(.*?)(?=\n|Comment\s+2|$)",
        "Comment_2": r"Comment\s+2\s*?:\s*?(.*?)(?=\n|Comment\s+3|$)",
        "Comment_3": r"Comment\s+3\s*?:\s*?(.*?)(?=\n|Comment\s+4|$)",
        "Comment_4": r"Comment\s+4\s*?:\s*?(.*?)(?=\n|Next|$)",
        
        # Reporter information - handles both formats
        "Reported_By": r"(?:[Rr]eport(?:ed)?\s+by|Report\s+sent\s+by)\s*?:\s*?(.*?)(?=\n|$)",
    }

    # Parse the raw data into structured entries
    entries = []
    seen_schools = set()  # Track schools we've already added
    
    # Split by Kitchen or School markers
    raw_schools = re.split(r"(?=Kitchen\s*?:|SCHOOL\s*?:)", raw_text, flags=re.IGNORECASE)
    
    for school_data in raw_schools:
        if not school_data.strip():
            continue
        entry = {}
        for key, pattern in data_pattern.items():
            match = re.search(pattern, school_data, re.IGNORECASE | re.DOTALL)
            entry[key] = match.group(1).strip() if match else ""

        # Only add if we have at least a school name and it's not a duplicate
        if entry.get("School"):
            school_name_normalized = normalize_school_name(entry.get("School"))
            
            # Check if we've already seen this school (case-insensitive)
            if school_name_normalized not in seen_schools:
                seen_schools.add(school_name_normalized)
                entries.append(entry)
    
    return entries


# App layout with improved UI
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Food for Education - Data Extraction Dashboard", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
    ], style={'padding': '20px 20px 10px 20px', 'backgroundColor': '#f8f9fa'}),
    
    # Main content wrapper
    html.Div([
        # Left side - Input and Preview (75%)
        html.Div([
            # Input section
            html.Div([
                html.H4("Paste Raw Data", style={'color': '#2c3e50', 'marginBottom': '10px'}),
                dcc.Textarea(
                    id="raw-data-input",
                    placeholder="Paste the school report data here...",
                    style={
                        "width": "100%", 
                        "height": "250px",
                        "border": "2px solid #3498db",
                        "borderRadius": "5px",
                        "padding": "10px",
                        "fontSize": "14px",
                        "fontFamily": "monospace"
                    }
                ),
                html.Button(
                    "Extract Data", 
                    id="extract-button", 
                    n_clicks=0,
                    style={
                        'marginTop': '10px',
                        'backgroundColor': '#3498db',
                        'color': 'white',
                        'border': 'none',
                        'padding': '10px 20px',
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'fontSize': '16px',
                        'width': '100%'
                    }
                ),
            ], style={
                "padding": "15px",
                "backgroundColor": "white",
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                "marginBottom": "15px"
            }),

            # Preview section
            html.Div([
                html.H4("Extracted Data Preview (Editable)", style={'color': '#2c3e50', 'marginBottom': '10px'}),
                dash_table.DataTable(
                    id="data-table",
                    columns=[{"name": col.replace("_", " "), "id": col} for col in [
                        "Kitchen", "School", "Date", "Menu", "Projected_Kids", "Actual_Meals_Served",
                        "Successful_Taps", "F4E_Supported_Kids", "Teachers", "Staff_Meals",
                        "Failed_Taps", "New_Registrations", "New_Tags_Replaced",
                        "Rice_Remaining", "B_W_G_Remaining", "Missed_Food", 
                        "Start_Taping", "Stop_Taping",
                        "Next_Day_Projection_Students", "Next_Day_Projection_Teachers", 
                        "Next_Day_Projection_Staff", "Projection_Comment", 
                        "Comment_1", "Comment_2", "Comment_3", "Comment_4", 
                        "Reported_By",
                    ]],
                    editable=True,
                    row_deletable=True,
                    style_table={"overflowX": "auto", "maxHeight": "350px", "overflowY": "auto"},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                        'fontSize': '12px',
                        'fontFamily': 'Arial',
                        'minWidth': '100px',
                        'whiteSpace': 'normal',
                        'height': 'auto',
                    },
                    style_header={
                        'backgroundColor': '#3498db',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'textAlign': 'center'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f8f9fa'
                        }
                    ]
                ),
                html.Button(
                    "Save Entry", 
                    id="save-button", 
                    n_clicks=0,
                    style={
                        'marginTop': '10px',
                        'backgroundColor': '#27ae60',
                        'color': 'white',
                        'border': 'none',
                        'padding': '10px 20px',
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'fontSize': '16px',
                        'width': '100%'
                    }
                ),
            ], style={
                "padding": "15px",
                "backgroundColor": "white",
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
            }),
        ], style={
            "width": "74%", 
            "display": "inline-block", 
            "verticalAlign": "top",
            "paddingRight": "10px"
        }),
        
        # Right side - School Tracking (25%)
        html.Div([
            html.Div([
                html.H4("School Tracking", style={'color': '#2c3e50', 'marginBottom': '10px'}),
                html.Div([
                    html.Div([
                        html.Span("Pending: ", style={'fontWeight': 'bold', 'color': '#e74c3c'}),
                        html.Span(id='pending-count', children='0'),
                    ], style={'display': 'inline-block', 'marginRight': '15px'}),
                    html.Div([
                        html.Span("Done: ", style={'fontWeight': 'bold', 'color': '#27ae60'}),
                        html.Span(id='completed-count', children='0'),
                    ], style={'display': 'inline-block'}),
                ], style={'marginBottom': '10px', 'fontSize': '14px'}),
                html.Div(id='school-checklist-container', style={
                    'border': '2px solid #3498db',
                    'borderRadius': '8px',
                    'padding': '10px',
                    'backgroundColor': '#ecf0f1',
                    'maxHeight': '665px',
                    'overflowY': 'auto',
                    'fontSize': '13px'
                }),
            ], style={
                "padding": "15px",
                "backgroundColor": "white",
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                "height": "100%"
            })
        ], style={
            "width": "25%", 
            "display": "inline-block", 
            "verticalAlign": "top",
        }),
    ], style={"padding": "10px 20px"}),

    # Saved entries section
    html.Div([
        html.Div([
            html.H3("Saved Entries", style={'color': '#2c3e50', 'display': 'inline-block'}),
            html.Span(id='saved-count', children=' (0 entries)', 
                     style={'color': '#7f8c8d', 'marginLeft': '10px', 'fontSize': '18px'}),
        ]),
        dash_table.DataTable(
            id="saved-data-table",
            columns=[{"name": col.replace("_", " "), "id": col} for col in [
                "Kitchen", "School", "Date", "Menu", "Projected_Kids", "Actual_Meals_Served",
                "Successful_Taps", "F4E_Supported_Kids", "Teachers", "Staff_Meals",
                "Failed_Taps", "New_Registrations", "New_Tags_Replaced",
                "Rice_Remaining", "B_W_G_Remaining", "Missed_Food", 
                "Start_Taping", "Stop_Taping",
                "Next_Day_Projection_Students", "Next_Day_Projection_Teachers", 
                "Next_Day_Projection_Staff", "Projection_Comment", 
                "Comment_1", "Comment_2", "Comment_3", "Comment_4", 
                "Reported_By",
            ]],
            editable=True,
            row_deletable=True,
            style_table={"overflowX": "auto"},
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'fontSize': '12px',
                'fontFamily': 'Arial',
                'minWidth': '100px',
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_header={
                'backgroundColor': '#2c3e50',
                'color': 'white',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f8f9fa'
                }
            ]
        ),
        html.Button(
            "📥 Download CSV", 
            id="download-csv-button", 
            n_clicks=0,
            style={
                'marginTop': '10px',
                'backgroundColor': '#e67e22',
                'color': 'white',
                'border': 'none',
                'padding': '10px 20px',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontSize': '16px'
            }
        ),
        dcc.Download(id="download-csv"),
    ], style={
        "marginTop": "20px",
        "padding": "20px",
        "backgroundColor": "white",
        "borderRadius": "8px",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
    }),
    
    # Store for tracking completed schools
    dcc.Store(id='completed-schools', data=[]),
    dcc.Store(id='saved-data-store', data=[])
])

# Callback to update school checklist
@app.callback(
    [Output('school-checklist-container', 'children'),
     Output('pending-count', 'children'),
     Output('completed-count', 'children')],
    [Input('completed-schools', 'data')]
)
def update_school_checklist(completed_schools):
    completed_schools = completed_schools or []
    
    # Separate pending and completed schools
    pending = [s for s in SCHOOLS_LIST if s not in completed_schools]
    completed = [s for s in SCHOOLS_LIST if s in completed_schools]
    
    # Create checklist items
    checklist_items = []
    
    # Pending schools (top)
    for school in pending:
        checklist_items.append(
            html.Div([
                html.Span("☐ ", style={'color': '#e74c3c', 'fontSize': '16px', 'marginRight': '8px'}),
                html.Span(school, style={'color': '#2c3e50'})
            ], style={'padding': '6px', 'borderBottom': '1px solid #ddd'})
        )
    
    # Completed schools (bottom)
    for school in completed:
        checklist_items.append(
            html.Div([
                html.Span("☑ ", style={'color': '#27ae60', 'fontSize': '16px', 'marginRight': '8px'}),
                html.Span(school, style={'color': '#95a5a6', 'textDecoration': 'line-through'})
            ], style={'padding': '6px', 'borderBottom': '1px solid #ddd', 'backgroundColor': '#d5f4e6'})
        )
    
    return checklist_items, str(len(pending)), str(len(completed))

# Callback to extract data
@app.callback(
    Output("data-table", "data"),
    Input("extract-button", "n_clicks"),
    State("raw-data-input", "value")
)
def update_table(n_clicks, raw_text):
    if n_clicks > 0 and raw_text:
        extracted = extract_data(raw_text)
        return extracted
    return []

# Callback to save entry and update completed schools
@app.callback(
    [Output("saved-data-table", "data"),
     Output("saved-data-store", "data"),
     Output("completed-schools", "data"),
     Output("raw-data-input", "value"),
     Output("saved-count", "children")],
    Input("save-button", "n_clicks"),
    [State("data-table", "data"),
     State("saved-data-store", "data"),
     State("completed-schools", "data")]
)
def save_entry(n_clicks, current_entry, saved_data, completed_schools):
    if n_clicks > 0 and current_entry:
        saved_data = saved_data or []
        completed_schools = completed_schools or []
        
        # Add new entries to memory
        new_saved = saved_data + current_entry
        
        # Update completed schools with better matching
        for entry in current_entry:
            school_name = entry.get('School', '')
            if school_name:
                normalized_entry = normalize_school_name(school_name)
                
                # Check if school matches any in our list
                for tracked_school in SCHOOLS_LIST:
                    normalized_tracked = normalize_school_name(tracked_school)
                    
                    # Match if normalized names are similar
                    if normalized_tracked in normalized_entry or normalized_entry in normalized_tracked:
                        if tracked_school not in completed_schools:
                            completed_schools.append(tracked_school)
                            break
        
        saved_count = f" ({len(new_saved)} entries)"
        
        # Clear the input after saving
        return new_saved, new_saved, completed_schools, "", saved_count
    
    saved_data = saved_data or []
    saved_count = f" ({len(saved_data)} entries)"
    return saved_data, saved_data, completed_schools or [], dash.no_update, saved_count

# Callback to download CSV.
@app.callback(
    Output("download-csv", "data"),
    Input("download-csv-button", "n_clicks"),
    State("saved-data-store", "data")
)
def download_csv(n_clicks, table_data):
    if n_clicks > 0 and table_data:
        df = pd.DataFrame(table_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return dcc.send_data_frame(df.to_csv, f"f4e_data_{timestamp}.csv", index=False)
    return dash.no_update

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)