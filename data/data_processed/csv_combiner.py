import pandas as pd
import glob
import os

# Directory where cleaned CSVs are saved
input_dir = "/opt/airflow/data/data_processed"

# Remove old combined files first
for old in glob.glob(os.path.join(input_dir, "df_upto_*.csv")):
    os.remove(old)

# Load all cleaned CSVs
files = glob.glob(os.path.join(input_dir, "*_clean.csv"))

df_list = []

month_map = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

for f in files:
    temp = pd.read_csv(f)
    date_str = os.path.basename(f).replace("_clean.csv", "")
    parts = date_str.split("_")
    if len(parts) == 3:
        month_abbr, day, year = parts   # <-- correct order
        m_num = month_map[month_abbr.lower()]
        parsed_date = pd.to_datetime(f"20{year}-{m_num}-{day}", errors="coerce")
    else:
        parsed_date = pd.NaT
    temp["file_date"] = parsed_date
    df_list.append(temp)

if not df_list:
    raise FileNotFoundError(f"No *_clean.csv files found in {input_dir}")

# Combine and sort
combined_df = pd.concat(df_list, ignore_index=True).sort_values("file_date")

# Get last file date for naming convention
last_date = combined_df["file_date"].max()
last_name = last_date.strftime("%b_%d_%y").lower()

# Save new combined file
output_file = os.path.join(input_dir, f"df_upto_{last_name}.csv")
combined_df.to_csv(output_file, index=False)

print(f"Saved combined dataset as {output_file}")
