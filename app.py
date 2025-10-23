import streamlit as st
import pandas as pd
from utils.excel_utils import initialize_excel, append_record, load_data
from io import BytesIO 
import os

st.set_page_config(page_title="Nurse Attendance Tracker", layout="wide")
st.title("👩‍⚕️ Nurse Attendance & Deviation Tracker")

# Initialize Excel file
initialize_excel()

st.sidebar.header("Add Attendance Record")
nurse_name = st.sidebar.text_input("Nurse Name")
date = st.sidebar.date_input("Date")
status = st.sidebar.selectbox("Status", ["A", "M", "N", "WO", "NO", "FL", "NH", "L"])
ward = st.sidebar.text_input("Ward (if present)")

if st.sidebar.button("Save Record"):
    if nurse_name:
        append_record(nurse_name, date, status, ward)
        st.sidebar.success(f"Record added for {nurse_name} on {date}")
    else:
        st.sidebar.error("Please enter Nurse Name before saving.")

# Load data and display
st.subheader("📋 Attendance Data")
data = load_data()
st.dataframe(data, use_container_width=True)

# Optional: Deviation calculation
st.subheader("📊 Deviation Summary")
if not data.empty:
    deviation_df = data.copy()
    deviation_df['Absent'] = deviation_df['Status'].isin(['WO', 'NO', 'L', 'FL', 'NH'])
    summary = (
        deviation_df.groupby('Nurse Name')
        .agg(Total_Days=('Date', 'count'),
             Absent_Days=('Absent', 'sum'))
        .reset_index()
    )
    summary['Deviation %'] = (summary['Absent_Days'] / summary['Total_Days']) * 100
    st.dataframe(summary)

st.subheader("⬇️ Download Attendance File")

excel_path = os.path.join("data", "attendance_data.xlsx")
if os.path.exists(excel_path):
    with open(excel_path, "rb") as f:
        st.download_button(
            label="Download Attendance Excel",
            data=f,
            file_name="attendance_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("No attendance file found yet. Add some records first.")
