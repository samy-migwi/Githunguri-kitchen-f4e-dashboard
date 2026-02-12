import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import re

# Initialize the app
app = dash.Dash(__name__)

# Helper function to extract data
def extract_data(raw_text):
    # Define patterns for extraction
    data_pattern = {
    # General Information
    "School": r"SCHOOL\s*?:\s*?(.*?)\n",
    "Date": r"Date\s*?:\s*?(.*?)\n",
    "Menu": r"Menu\s*?:\s*?(.*?)\n",
    "Projected_Kids": r"Projected\s+no\s+of\s+kids\s*?:\s*?(\d+)",
    "Actual_Meals_Served": r"Actual\s+meals\s+served\s*?:\s*?(\d+)",
    "Successful_Taps": r"Successful\s+Taps\s*?:\s*?(\d+)",
    "F4E_Supported_Kids": r"F4E\s+Supported\s+Kids\s*?:\s*?([\d+\(\)]+)",
    "Teachers": r"Teachers\s*?:\s*?(\d+)",
    "Staff_Meals": r"Staff\s+meals\s*?:\s*?(\d+)",
    "Failed_Taps": r"Failed\s+taps\s*?:\s*?(\d+)",
    "New_Registrations": r"New\s+registrations\s*?:\s*?(\d+)",
    "New_Tags_Replaced": r"New\s+tags\s+replaced\s*?:\s*?(\d+)",

    # Food received section
    "Rice_Received": r"Food\s+received.*?\n.*?Rice[^\d]*(\d+)",
    "B_W_G_Received": r"Food\s+received.*?\n(?:.*?Rice[^\d]*\d+kgs.*?\n)*?.*?(?:Beans|GreenGrams|Western|G.G)[^\d]*(\d+)",

    # Excess food section
    "Rice_Excess": r"Excess.*?\n.*?Rice[^\d]*(\d+\.?\d*)",
    "B_W_G_Excess": r"Excess.*?\n(?:.*?Rice[^\d]*\d+kgs.*?\n)*?.*?(?:Beans|GreenGrams|Western|G.G)[^\d]*(\d+)",

    # Food remaining section
    "Rice_Remaining": r"Food\s+remaining.*?\n.*?Rice[^\d]*(\d+\.?\d*)",
    "B_W_G_Remaining": r"Food\s+remaining.*?\n(?:.*?Rice[^\d]*\d+kgs.*?\n)*?.*?(?:Beans|GreenGrams|Western|G.G|Wairimu)[^\d]*(\d+)",

    # Temperatures
    "B_W_G_Temperatures": r"Average\s+Temp\s+for\s+(?:Beans|GreenGrams|Western|G.G|GG)\s*?:\s*?(\d+\.?\d*)°[Cc]",
    "Rice_Temp": r"Average\s+Temp\s+for\s+(?:[Ww]hite|[Tt]umeric)?\s*[Rr]ice\s*?:\s*?(\d+\.?\d*)°[Cc]",
                      
    # Other Information
    "Missed_Food": r"No\s+of\s+kids\s+missed\s+food\s*?:\s*?(\d+)",
    "Next_Day_Projection": r"(?:Food\s+Projection|Next\s+Day's\s+Food\s+Projection|Primary\s+School)\s*?:\s*?(\d+)",

    # Time food arrival
    "Food_Arrival_Time": r"Food\s+arrival\s*?:\s*?(\d{1,2}:\d{2}(?:am|pm)?|\d{4}[Hh]rs)",
    "Start_Taping": r"Started\s+tapping\s+at\s*?:\s*?(\d{1,2}:\d{2}(?:am|pm)?|\d{4}[Hh]rs)",
    "Stop_Taping": r"Started\s+tapping\s+at\s+.*?to\s*?(\d{1,2}:\d{2}(?:am|pm)?|\d{4}[Hh]rs)",

    # Comments
    "Projection_Comment": r"\*?Comment\s+on\s+projection\s*?:\s*?(.*?)\n",
    "Comment_1": r"\*?Comment\s+1\s*?:\s*?(.*?)\n",
    "Comment_2": r"\*?Comment\s+2\s*?:\s*?(.*?)\n",
    "Comment_3": r"\*?Comment\s+3\s*?:\s*?(.*?)\n",
    "Comment_4": r"\*?Comment\s+4\s*?:\s*?(.*?)\n",
    "Reported_By": r"[Rr]eport(?:ed)?\s+by\s*?:\s*?(.*?)\n"
}

    

    def safe_float(value):
        """Safely convert a value to float, defaulting to 0.0 if empty or invalid."""
        try:
            return float(value) if value else 0.0
        except ValueError:
            return 0.0

    # Parse the raw data into structured entries
    entries = []
    raw_schools = re.split(r"(?=SCHOOL ?:)", raw_text)  # Split by school entries
    for school_data in raw_schools:
        if not school_data.strip():
            continue
        entry = {}
        for key, pattern in data_pattern.items():
            match = re.search(pattern, school_data, re.IGNORECASE | re.DOTALL)
            entry[key] = match.group(1).strip() if match else ""

        # Safely handle "Food Remaining" conversion
        rice_remaining = safe_float(entry.get("Rice Remaining", ""))
        bwg_remaining = safe_float(entry.get("B_W_G_Remaining", ""))
        entry["Food Remaining"] = f"Rice: {rice_remaining:.1f} kgs\nB_W_G: {bwg_remaining:.1f} kgs"

        entries.append(entry)
    return entries


# App layout
app.layout = html.Div([
    html.Div([
        dcc.Textarea(
            id="raw-data-input",
            placeholder="Paste the data here...",
            style={"width": "100%", "height": "200px"}
        ),
        html.Button("Extract Data", id="extract-button", n_clicks=0),
    ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}),

    html.Div([
        dash_table.DataTable(
            id="data-table",
            columns=[{"name": col, "id": col} for col in [
                "School", "Date", "Menu", "Projected_Kids", "Actual_Meals_Served",
                "Successful_Taps", "F4E_Supported_Kids", "Teachers", "Staff_Meals",
                "Failed_Taps", "New_Registrations", "New_Tags_Replaced",
                "Rice_Received", "B_W_G_Received", "Rice_Excess", "B_W_G_Excess",
                "Rice_Temp", "B_W_G_Temperatures", "Rice_Remaining", "B_W_G_Remaining","Missed_Food", "Food_Arrival_Time","Start_Taping","Stop_Taping",
                "Next_Day_Projection", "Projection_Comment", "Comment_1", "Comment_2", "Comment_3", "Comment_4", 
                "Reported_By",
            ]],
            editable=True,
            row_deletable=True,
            style_table={"overflowX": "auto"}
        ),
        html.Button("Save Entry", id="save-button", n_clicks=0),
    ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}),

    html.Div([
        html.H4("Saved Entries"),
        dash_table.DataTable(
            id="saved-data-table",
            columns=[{"name": col, "id": col} for col in [
                "School", "Date", "Menu", "Projected_Kids", "Actual_Meals_Served",
                "Successful_Taps", "F4E_Supported_Kids", "Teachers", "Staff_Meals",
                "Failed_Taps", "New_Registrations", "New_Tags_Replaced",
                "Rice_Received", "B_W_G_Received", "Rice_Excess", "B_W_G_Excess",
                "Rice_Temp", "B_W_G_Temperatures", "Rice_Remaining", "B_W_G_Remaining","Missed_Food","Food_Arrival_Time","Start_Taping","Stop_Taping",
                "Next_Day_Projection", "Projection_Comment", "Comment_1", "Comment_2", "Comment_3", "Comment_4", 
                "Reported_By",
            ]],
            editable=True,
            row_deletable=True,
            style_table={"overflowX": "auto"}
        ),
        html.Button("Download CSV", id="download-csv-button", n_clicks=0),
        dcc.Download(id="download-csv"),
    ], style={"marginTop": "20px"})
])

# Callbacks
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

@app.callback(
    Output("saved-data-table", "data"),
    Input("save-button", "n_clicks"),
    State("data-table", "data"),
    State("saved-data-table", "data")
)
def save_entry(n_clicks, current_entry, saved_entries):
    if n_clicks > 0 and current_entry:
        saved_entries = saved_entries or []
        return saved_entries + current_entry
    return saved_entries

@app.callback(
    Output("download-csv", "data"),
    Input("download-csv-button", "n_clicks"),
    State("saved-data-table", "data")
)
def download_csv(n_clicks, table_data):
    if n_clicks > 0 and table_data:
        df = pd.DataFrame(table_data)
        return dcc.send_data_frame(df.to_csv, "saved_entries.csv")
    return dash.no_update

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
    