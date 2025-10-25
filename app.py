import streamlit as st
import pandas as pd
from utils.excel_processor import load_excel, calculate_all_deviations, save_excel
from utils.data_models import NurseData
import os

st.title("Nurse Deviation Tracker - Palliative Center")

DATA_FILE = os.path.join("data", "nurse_data.xlsx")
os.makedirs("data", exist_ok=True)

nurses = {}

# --- STEP 1: Load existing Excel if available ---
if os.path.exists(DATA_FILE):
    nurses = load_excel(DATA_FILE)
    st.info(f"Loaded existing data from {DATA_FILE}")

# --- STEP 2: Optional upload to replace data ---
uploaded_file = st.file_uploader("Upload Excel file (optional)", type=["xlsx"])
if uploaded_file:
    with open(DATA_FILE, "wb") as f:
        f.write(uploaded_file.getvalue())
    nurses = load_excel(DATA_FILE)
    st.success("File uploaded and replaced successfully!")

# --- STEP 3: Manual data entry ---
st.header("Add / Update Nurse Data Manually")

nurse_name = st.text_input("Nurse Name")
date = st.date_input("Date")
is_present = st.radio("Status", ["Present", "Absent"])

if is_present == "Present":
    ward = st.text_input("Ward")
    actual = st.selectbox("Shift", ["M", "A", "N"])
else:
    actual = st.selectbox("Leave Type", ["NO", "WO", "PH", "NH", "L", "Other"])
    ward = None

if st.button("Add Record"):
    if nurse_name and date:
        if nurse_name not in nurses:
            nurses[nurse_name] = NurseData(nurse_name)
        nurses[nurse_name].add_record(
            date=str(date),
            planned="",  # planned left blank for manual entries
            actual=actual,
            ward=ward
        )

        df = calculate_all_deviations(nurses)
        save_excel(df, DATA_FILE)
        st.success(f"Record added successfully and saved to {DATA_FILE}!")
    else:
        st.error("Please fill in Nurse Name and Date.")

# --- STEP 4: Generate or Update Report ---
if nurses and st.button("Generate / Update Deviation Report"):
    df = calculate_all_deviations(nurses)
    save_excel(df, DATA_FILE)
    st.success(f"Deviation report updated successfully")

    with open(DATA_FILE, "rb") as f:
        st.download_button("Download Updated Report", f, file_name="nurse_deviation_report.xlsx")
