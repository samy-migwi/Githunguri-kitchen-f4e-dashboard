import pandas as pd
import glob
import os

# Remove old combined files first
for old in glob.glob("df_upto_*.csv"):
    os.remove(old)

# Load all cleaned CSVs
files = glob.glob("*_clean.csv")

df_list = []

# Month mapping for filename parsing
month_map = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

for f in files:
    temp = pd.read_csv(f)

    # Extract date from filename (e.g. "feb_24_26_clean.csv")
    date_str = os.path.basename(f).replace("_clean.csv", "")
    parts = date_str.split("_")

    if len(parts) == 3:
        month, day, year = parts
        month_num = month_map.get(month.lower(), 1)
        # Convert to proper datetime (assume year is 20xx)
        parsed_date = pd.to_datetime(f"20{year}-{month_num}-{day}", errors="coerce")
    else:
        parsed_date = pd.NaT

    temp["file_date"] = parsed_date
    df_list.append(temp)

# Combine all dataframes and sort by file_date
combined_df = pd.concat(df_list, ignore_index=True).sort_values("file_date")

# Get last file date for naming convention
last_date = combined_df["file_date"].max()
last_name = last_date.strftime("%b_%d_%y").lower()

# Save new combined file
output_file = f"df_upto_{last_name}.csv"
combined_df.to_csv(output_file, index=False)

print(f"Saved combined dataset as {output_file}")
