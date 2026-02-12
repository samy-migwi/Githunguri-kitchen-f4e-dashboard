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
        "School": r"SCHOOL ?: ?(.*?)\n",
        "Date": r"Date ?: ?(.*?)\n",
        "Menu": r"Menu ?: ?(.*?)\n",
        "Projected Kids": r"Projected no of kids ?: ?(\d+)",
        "Actual Meals Served": r"Actual meals served ?: ?(\d+)",
        "Successful Taps": r"Successful Taps ?: ?(\d+)",
        "F4E Supported Kids": r"F4E Supported Kids ?: ?([\d+\(\)]+)",
        "Teachers": r"Teachers ?: ?(\d+)",
        "Staff Meals": r"Staff meals ?: ?(\d+)",
        "Failed Taps": r"Failed taps ?: ?(\d+)",
        "New Registrations": r"New registrations ?: ?(\d+)",
        "New Tags Replaced": r"New tags replaced ?: ?(\d+)",

        # Food received section
        "Rice Received": r"Food received.*?\n.*?Rice[^\d]*(\d+)",
        "B_W_G_Received": r"(?:Beans|GreenGrams|Western):\s*(\d+)",
        
        #r"Food received.*?\n(?:.*?\n)*?(Beans|GreenGrams|Western):\s*(\d+)"
                        
          
        # Excess food section
        "Rice Excess": r"Excess.*?\n.*?Rice[^\d]*(\d+\.?\d*)",
        "B_W_G_Excess": r"Excess.*?\n.*?(Beans|GreenGrams|Western)[^\d]*(\d+\.?\d*)",

        # Food remaining section
        "Rice Remaining": r"Food remaining.*?\n.*?Rice[^\d]*(\d+\.?\d*)",
        "B_W_G_Remaining": r"Food remaining.*?\n.*?(Beans|GreenGrams|Western)[^\d]*(\d+\.?\d*)",

        # Temperatures
        "B_W_G_Temperatures": r"Average Temp for (?:Beans|GreenGrams|Western) ?: ?(\d+\.?\d*)°[Cc]",
        "Rice Temp": r"Average Temp for Rice ?: ?(\d+\.?\d*)°[Cc]",

        # Other Information
        "Missed Food": r"No of kids missed food ?: ?(\d+)",
        "Next Day Projection": r"\*?Next Day's Food Projection ?: ?(\d+)",
        "Projection Comment": r"\*?Comment on projection ?: ?(.*?)\n",
        "Comment 1": r"\*?Comment 1 ?: ?(.*?)\n",
        "Comment 2": r"\*?Comment 2 ?: ?(.*?)\n",
        "Comment 3": r"\*?Comment 3 ?: ?(.*?)\n",
        "Comment 4": r"\*?Comment 4 ?: ?(.*?)\n",
        "Reported By": r"Report by ?: ?(.*?)\n"
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

        # Ensure "Food Remaining" fields are correctly placed after "Excess Food"
        rice_remaining = safe_float(entry.get("Rice Remaining", ""))
        bwg_remaining = safe_float(entry.get("B_W_G_Remaining", ""))

        # Format "Food Remaining" section similar to "Food Received"
        entry["Food Remaining"] = {
            "Rice Remaining": int(rice_remaining),
            "B_W_G_Remaining": int(bwg_remaining)
        }

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
                "School", "Date", "Menu", "Projected Kids", "Actual Meals Served",
                "Successful Taps", "F4E Supported Kids", "Teachers", "Staff Meals",
                "Failed Taps", "New Registrations", "New Tags Replaced",
                "Rice Received", "B_W_G_Received", "Rice Excess", "B_W_G_Excess",
                "Rice Temp", "B_W_G_Temperatures", "Missed Food",
                "Next Day Projection", "Projection Comment", "Comment 1", "Comment 2", "Comment 3", "Comment 4", 
                "Reported By", "Food Remaining"
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
                "School", "Date", "Menu", "Projected Kids", "Actual Meals Served",
                "Successful Taps", "F4E Supported Kids", "Teachers", "Staff Meals",
                "Failed Taps", "New Registrations", "New Tags Replaced",
                "Rice Received", "B_W_G_Received", "Rice Excess", "B_W_G_Excess",
                "Rice Temp", "B_W_G_Temperatures", "Missed Food",
                "Next Day Projection", "Projection Comment", "Comment 1", "Comment 2", "Comment 3", "Comment 4",
                "Reported By", "Food Remaining"
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
