import pandas as pd
import numpy as np
import re
import os
import glob

#data importing
#date="feb_24_26.csv"
#df=pd.read_csv(fr"C:\Users\Administrator\Desktop\ds\f4e\githunguri1\Githunguri-kitchen-f4e-dashboard\data\data_raw\extarcted_csv\{date}")


# Input directory
input_dir ="/opt/airflow/data/data_raw/extarcted_csv"


# Find all CSVs
files = glob.glob(os.path.join(input_dir, "*.csv"))

if not files:
    raise FileNotFoundError("No CSV files found in the directory.")

# Pick the latest file (or loop if you want all)
latest_file = max(files, key=os.path.getmtime)

# Load into DataFrame
df = pd.read_csv(latest_file)
print(f"Successfully loaded: {os.path.basename(latest_file)}")

# Extract base name for later export
base = os.path.splitext(os.path.basename(latest_file))[0]


#functions
def clean_school_name(name):
    # Fixing  this typos for mathanja 
    name = name.replace("Primry", "Primary")
    
    # Replacing "Comprehensive" with "Primary"
    name = name.replace("Comprehensive", "Primary")
    
    # chopping the word "School" 
    name = re.sub(r"\b[Ss]chool\b", "", name)
    
    # remaoving  Junior Secondary" or similar suffixes
    name = re.sub(r"& Junior Secondary", "", name, flags=re.IGNORECASE)
    
    
    # Simplifying Catholic Archdiocese   and pcea
    if "Gataka" in name:
        return "Gataka Primary"
    if "Mitahato" in name:
        if "Secondary" in name:
            return "Mitahato Secondary"
        else:
            return "Mitahato Primary"
    if "Matuguta" in name:
        if "Secondary" in name:
            return "Matuguta Secondary"
        else:
            return "Matuguta Primary"
    if "Riamute" in name:
        return "Riamute Primary"
    if "Ngemwa" in name:
        if "Secondary" in name:
            return "Ngemwa Secondary"
        else:
            return "Ngemwa Primary"
    if "Lioki" in name:
        if "Secondary" in name:
            return "Lioki Secondary"
        else:
            return "Lioki Primary"
    if "Karia" in name:
        if "Secondary" in name:
            return "Karia Secondary"
        else:
            return "Karia Primary"
    if "Kamondo" in name:
        if "Secondary" in name:
            return "Kamondo Secondary"
        else:
            return "Kamondo Primary"
    if "Githunguri" in name:
        if "Secondary" in name:
            return "Githunguri Tech Secondary"
        else:
            return "Githunguri Primary"
    if "Mathanja" in name:
        return "Mathanja Primary"
    if "Kagema" in name:
        if "Secondary" in name:
            return "Kagema Secondary"
        else:
            return "Kagema Primary"
    
    
    
    #    spacing and capitalization
    name = " ".join(name.split())  # remove extra spaces
    name = name.title()            # standardize case
    
    return name.strip()

df["School"] = df["School"].apply(clean_school_name)
#Going to moth of feb "Mukua Secondary" shift to kiambu kitchen   then we have a new school kagema primary serving from githunguri kitchen
githunguri_kitchen_schools= [
    "Kigumo Secondary",
    "Kigumo Primary",
    "Mukuyu Secondary",
    "Ihiga Primary",
    "Gathaithi Primary",
    "Githioro Primary",
    "Kindiga Primary",
    "Gitiha Secondary",
    "Gatitu Primary",
    "Kanyore Primary",
    "Matuguta Primary",
    "Mathanja Primary",
    "Gathaithi Secondary",
    "Gikang'A Kageche Secondary",
    "Matuguta Secondary",
    "Kiambururu Secondary",
    "Githiga Primary",
    "Gathangari Primary",
    "Gathiruini Primary",
    "Kiambururu Primary",
    "Thuita Secondary",
    "Kibichoi Primary",
    "Gatina Primary",
    "Gitombo Primary",
    "Kihuririo Primary",
    "Miiri Secondary",
    "Kiawaiguru Primary",
    "Kambui Primary",
    "Miguta Secondary",
    "Miguta Primary",
    "Ngewa Primary",
    "Mitahato Primary",
    "Gathugu Secondary",
    "Ndireti Secondary",
    "Giathieko Primary",
    "Ikinu Primary",
    "Kanjai Primary",
    "Mitahato Secondary",
    "Nyaga Primary",
    "Nyaga Secondary",
    "Riamute Primary",
    "Gathugu Primary",
    "Komothai Primary",
    "Kagema Secondary",
    "Kagema Primary",
    "Thuita Primary",
    "Miiri Primary",
    "Githima Primary",
    "William Ng'Iru Secondary",
    "Njunu Primary",
    "Kanjai Secondary",
    "Ndireti Primary",
    "Gataka Primary",
    "Kiawairia Primary",
    "Kiawairia Secondary"
]

kiambu_kitchen_schools = [
    "Karia Secondary",
    "Riara Primary",
    "Mukua Secondary",
    "Gathanji Secondary",
    "Ngemwa Primary",
    "Ting'Ang'A Secondary",
    "Cianda Secondary",
    "Lioki Primary",
    "Ndumberi Primary",
    "St. Joseph Riabai Secondary",
    "Mungai Chengecha Primary",
    "Maciri Primary",
    "Kiairia Secondary",
    "Gicoco Primary",
    "St. Peters Ndumberi Secondary",
    "Ack Riabai Primary",
    "Ting'Ang'A Model",
    "Lioki Secondary",
    "Kawaida Secondary",
    "Githunguri Tech Secondary",
    "Loreto Primary",
    "Kiababu Primary",
    "Benson Njau Primary",
    "Kibubuti Primary",
    "Hgm Ting'Ang'A Secondary",
    "Kawaida Primary",
    "Hgm Ting'Ang'A Primary",
    "Riara Secondary",
    "Karia Primary",
    "Chief Wandie Primary",
    "Ak Magugu Primary",
    "Kamondo Primary",
    "Kiairia Primary",
    "Ngemwa Secondary",
    "Githunguri Primary",
    "Kamondo Secondary",
    "Gatatha Primary",
    "Ciiko Primary",
    "Kahunira Secondary",
    "Kahunira Primary",
    "St. Augustine Gatono Primary",
    "Njenga Karume Primary",
    "Muongoiya Secondary",
    "Muchatha Secondary",
    "St. Joseph Gathanga Secondary",
    "Kiambaa Primary",
    "Gathanji Primary",
    "Mayuyu Primary",
    "Muchatha Primary",
    "Karuri Primary",
    "Kibathi Primary",
    "Muongoiya Primary"
]
# creating a new columns of  the kichen served for each school 

#kiambu_kitchen_schools=["Githunguri Tech Secondary","Ngemwa Primary","Mukua Secondary","Ngemwa Secondary","Gathanji Primary","Gathanji Secondary","Lioki Primary","Kahunira Primary","Ak Magugu Primary","Lioki Secondary","Githunguri Primary","Karia Secondary","Karia Primary", "Ciiko Primary","Kiairia Secondary", "Kiairia Primary","Kahunira Secondary","Kamondo Secondary","Kamondo Primary", "Kiababu Primary"]
def map_kitchen_served(school_name):
    if school_name in kiambu_kitchen_schools:
        return 'Kiambu kitchen'
    elif school_name in githunguri_kitchen_schools:
        return 'Githunguri kitchen'
    else:
        return 'No kitchen found'
df["Kitchen"] = df["School"].apply(map_kitchen_served)
#schools type 
def get_school_type(name):
    name = name.lower()
    if "secondary" in name:
        return "Secondary"
    else:
        return "Primary"

df["School_Type"] = df["School"].apply(get_school_type)

#for good visual  i rearrabge the columns so school type can be be next to school name
cols = list(df.columns)
cols.insert(2, cols.pop(cols.index("School_Type")))
df = df[cols]
#region columns
Githunguri_1=["Kahunira Secondary","Ciiko Primary","Mukuyu Secondary","Kiawaiguru Primary","Gitiha Secondary","Kiawairia Primary","Matuguta Primary","Kindiga Primary","Gathiruini Primary","Kahunira Primary","Njunu Primary","Githima Primary","Kiawairia Secondary","Githioro Primary","Ihiga Primary","Kiambururu Primary","Gathaithi Secondary","Gathaithi Primary","Gatina Primary","Mathanja Primary","Gitombo Primary","Matuguta Secondary","Kanyore Primary","Kiambururu Secondary","Gikang'A Kageche Secondary","Gataka Primary","Githiga Primary","Kiababu Primary","Githunguri Tech Secondary","Gatitu Primary",]
Githunguri_2=["Karia Secondary","William Ng'Iru Secondary","Mukua Secondary","Mitahato Secondary","Ndireti Secondary","Mitahato Primary","Riamute Primary","Kanjai Primary","Komothai Primary","Miguta Primary","Ngewa Primary","Miiri Secondary","Nyaga Secondary","Nyaga Primary","Giathieko Primary","Miguta Secondary","Kambui Primary","Kanjai Secondary","Ndireti Primary","Miiri Primary","Ikinu Primary","Ak Magugu Primary","Kamondo Secondary","Kamondo Primary","","Lioki Primary","Gathangari Primary","Ngemwa Primary","Kiairia Secondary","Kiairia Primary","Githunguri Primary","Karia Primary","Lioki Secondary","Gathanji Secondary","Gathanji Primary","Ngemwa Secondary"]
Ruiru_Githunguri=["Gathugu Primary","Thuita Secondary","Kibichoi Primary","Gathugu Secondary","Kagema Secondary","Thuita Primary","Kigumo Secondary","Kigumo Primary","Kihuririo Primary","Kagema Primary"]

#new column for cluster 
def assign_cluster(school):
    if school in Githunguri_1:
        return "Githunguri 1"
    elif school in Githunguri_2:
        return "Githunguri 2"
    elif school in Ruiru_Githunguri:
        return "Ruiru-Githunguri"
    else:
        return "Kiambu Regions"

# Apply the function to the School column
df["Cluster"] = df["School"].apply(assign_cluster)

#for good visual  i re-arrange the columns so school type can be be next to school name
cols = list(df.columns)
cols.insert(2, cols.pop(cols.index("Cluster")))# outdo the previous setup of school type in the upper part of the code
df = df[cols]

#new column for month 
df["Date"] = pd.to_datetime(df["Date"], errors="coerce", format="mixed", dayfirst=True)
first_valid_date = df["Date"].dropna().iloc[0]
df["Date"] = df["Date"].fillna(first_valid_date)
df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.month
df["Month"] = df["Date"].dt.month_name()

cols = list(df.columns)
cols.insert(3, cols.pop(cols.index("Month")))
df = df[cols]

def get_rice_variant(menu_item):
    if pd.isna(menu_item):
        return ""
    menu_item = menu_item.lower()
    if "masala" in menu_item:
        return "Masala"
    elif "tumeric" in menu_item:
        return "Tumeric"
    else:
        return "White"

df["Rice_variant"] = df["Menu"].apply(get_rice_variant)
# For column reordering to be next to menu 
cols = list(df.columns)
cols.insert(5, cols.pop(cols.index("Rice_variant")))
df = df[cols]
def clean_menu(name):
    if pd.isna(name):
        return None
    
    # Normalize casing and whitespace
    name = name.strip().title()
    
    # Replace connectors
    name = name.replace("&", "And")
    
    # Standardize synonyms/abbreviations
    name = re.sub(r"\bGg\b", "Greengrams", name, flags=re.IGNORECASE)
    name = re.sub(r"\bG\.G\b", "Greengrams", name, flags=re.IGNORECASE)
    name = re.sub(r"Riceandgg", "Rice and Greengrams", name, flags=re.IGNORECASE)
    name = name.replace("Green Gram", "Greengrams")
    name = name.replace("Green Grams", "Greengrams")
    name = name.replace("Greengram", "Greengrams")
    
    # If "Rice" exists, discard everything before it
    if "Rice" in name:
        idx = name.find("Rice")
        name = name[idx:]
    
    # Canonical mapping
    if "Greengrams" in name:
        return "Rice and Greengrams"
    elif "Beans" in name:
        return "Rice and Beans"
    elif "Western" in name:
        return "Rice and Western"
    
    # If no keyword matched, return substring after Rice
    return name
df["Menu"] = df["Menu"].apply(clean_menu)
# Convert to datetime

df["Start_Taping"] = pd.to_datetime(df["Start_Taping"], errors="coerce", format="mixed")
df["Stop_Taping"]  = pd.to_datetime(df["Stop_Taping"], errors="coerce", format="mixed")
df["Start_Taping"] = pd.to_datetime(df["Start_Taping"], format="%d %b %Y, %H:%M:%S")
df["Stop_Taping"] = pd.to_datetime(df["Stop_Taping"], format="%d %b %Y, %H:%M:%S")
# Compute duration
lunch_time= df["Stop_Taping"] - df["Start_Taping"]
df["Lunch_Time_Min"] = (lunch_time.dt.total_seconds() / 60).round(0).astype('Int64')  # Convert to minutes and round


cols = list(df.columns)
# moving Lunch_Time_Min to index 23 nest to the parent columns
cols.insert(23, cols.pop(cols.index("Lunch_Time_Min")))

# Reassign DataFrame with new order
df = df[cols]

#lets use os 
output_dir ="/opt/airflow/data/data_processed"
#base = date.replace(".csv", "")
output_path = os.path.join(output_dir, f"{base}_clean.csv")
df.to_csv(output_path, index=False)
print("Saved:", output_path)