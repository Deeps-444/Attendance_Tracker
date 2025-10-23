import pandas as pd
import os

# Folder and file setup
DATA_DIR = "data"
FILE_PATH = os.path.join(DATA_DIR, "attendance_data.xlsx")

def initialize_excel():
    """Create the data folder and Excel file if missing."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(FILE_PATH):
        df = pd.DataFrame(columns=["Nurse Name", "Date", "Status", "Ward"])
        df.to_excel(FILE_PATH, index=False)

def append_record(nurse_name, date, status, ward):
    """Add a new record to the Excel sheet."""
    df = pd.read_excel(FILE_PATH)
    new_row = pd.DataFrame([{
        "Nurse Name": nurse_name,
        "Date": pd.to_datetime(date),
        "Status": status,
        "Ward": ward
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(FILE_PATH, index=False)

def load_data():
    """Load all records from the Excel sheet."""
    if os.path.exists(FILE_PATH):
        return pd.read_excel(FILE_PATH)
    else:
        return pd.DataFrame(columns=["Nurse Name", "Date", "Status", "Ward"])
