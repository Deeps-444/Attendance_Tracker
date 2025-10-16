import streamlit as st
from deviation_logic import load_and_transform_excel, calculate_deviations
from plotting import (
    analyze_deviation_types, analyze_deviation_trends,
    analyze_monthly_deviation, analyze_employee_performance,
    analyze_deviation_by_shift_type, analyze_shift_type_distribution
)

# Page config
st.set_page_config(page_title="Attendance Deviation", layout="wide")

# Load CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style.css")

# Title
st.title("🏥 Cipla Palliative Care - Nurse Attendance Deviation Analysis")
st.markdown("---")

# Upload files
col1, col2 = st.columns(2)
with col1:
    planned_file = st.file_uploader(" Upload Planned Shifts", type=['xlsx', 'xls'])
with col2:
    actual_file = st.file_uploader(" Upload Actual Shifts", type=['xlsx', 'xls'])

if planned_file and actual_file:
    planned_df = load_and_transform_excel(planned_file)
    actual_df = load_and_transform_excel(actual_file)
    
    if planned_df is not None and actual_df is not None:
        st.success("Files loaded successfully!")
        deviation_df = calculate_deviations(planned_df, actual_df)
        
        analysis_type = st.selectbox(
            "Select Analysis Type",
            [
                "Deviation Types Distribution",
                "Deviation Trends Over Time",
                "Date-wise Deviation Analysis",
                "Employee Performance Analysis",
                "Deviation by Shift Type",
                "Shift Type Distribution"
            ]
        )
        
        if analysis_type == "Deviation Types Distribution":
            st.plotly_chart(analyze_deviation_types(deviation_df), use_container_width=True)
        elif analysis_type == "Deviation Trends Over Time":
            fig = analyze_deviation_trends(deviation_df)
            if fig: st.plotly_chart(fig, use_container_width=True)
        elif analysis_type == "Date-wise Deviation Analysis":
            st.plotly_chart(analyze_monthly_deviation(deviation_df), use_container_width=True)
        elif analysis_type == "Employee Performance Analysis":
            fig, stats_df = analyze_employee_performance(deviation_df)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(stats_df)
        elif analysis_type == "Deviation by Shift Type":
            fig = analyze_deviation_by_shift_type(deviation_df)
            if fig: st.plotly_chart(fig, use_container_width=True)
        elif analysis_type == "Shift Type Distribution":
            st.plotly_chart(analyze_shift_type_distribution(deviation_df), use_container_width=True)
