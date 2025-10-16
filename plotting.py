# plotting.py
import plotly.express as px

# ------------------- Deviation Types -------------------
def analyze_deviation_types(df):
    df_filtered = df[df['Deviation_Type'] != 'No Record']
    deviation_counts = df_filtered['Deviation_Type'].value_counts()
    fig = px.pie(
        values=deviation_counts.values,
        names=deviation_counts.index,
        title="Distribution of Deviation Types",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

# ------------------- Deviation Trends -------------------
def analyze_deviation_trends(df):
    df_filtered = df[df['Has_Deviation']]
    if len(df_filtered) == 0:
        return None
    daily_deviations = df_filtered.groupby('Date').size().reset_index(name='Count')
    daily_deviations = daily_deviations.sort_values('Date')
    fig = px.line(
        daily_deviations,
        x='Date',
        y='Count',
        title="Deviation Trends Over Time",
        markers=True,
        color_discrete_sequence=['#3498db']
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="Number of Deviations")
    return fig

# ------------------- Monthly Deviations -------------------
def analyze_monthly_deviation(df):
    df_filtered = df[df['Deviation_Type'] != 'No Record']
    date_data = df_filtered.groupby(['Date', 'Deviation_Type']).size().reset_index(name='Count')
    date_data = date_data.sort_values('Date')
    fig = px.bar(
        date_data,
        x='Date',
        y='Count',
        color='Deviation_Type',
        title="Deviations by Date",
        barmode='stack',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    return fig

# ------------------- Employee Performance -------------------
def analyze_employee_performance(df):
    df_filtered = df[df['Deviation_Type'] != 'No Record']
    employee_stats = df_filtered.groupby('Employee_Name').agg({
        'Has_Deviation': 'sum',
        'Date': 'count'
    }).reset_index()
    employee_stats.columns = ['Employee_Name', 'Total_Deviations', 'Total_Shifts']
    employee_stats['Adherence_Rate'] = ((employee_stats['Total_Shifts'] - employee_stats['Total_Deviations']) / employee_stats['Total_Shifts'] * 100).round(2)
    employee_stats = employee_stats.sort_values('Adherence_Rate', ascending=True)
    fig = px.bar(
        employee_stats,
        x='Adherence_Rate',
        y='Employee_Name',
        orientation='h',
        title="Employee Adherence Rate (%)",
        color='Adherence_Rate',
        color_continuous_scale='RdYlGn',
        labels={'Adherence_Rate': 'Adherence Rate (%)'}
    )
    return fig, employee_stats

# ------------------- Deviations by Shift -------------------
def analyze_deviation_by_shift_type(df):
    df_filtered = df[df['Has_Deviation']]
    if len(df_filtered) == 0:
        return None
    shift_deviations = df_filtered.groupby('Shift_Type_Planned').size().reset_index(name='Count')
    shift_deviations = shift_deviations.sort_values('Count', ascending=False)
    fig = px.bar(
        shift_deviations,
        x='Shift_Type_Planned',
        y='Count',
        title="Deviations by Planned Shift Type",
        color='Count',
        color_continuous_scale='Reds'
    )
    fig.update_layout(xaxis_title="Planned Shift Type", yaxis_title="Number of Deviations")
    return fig

# ------------------- Actual Shift Distribution -------------------
def analyze_shift_type_distribution(df):
    df_filtered = df[df['Deviation_Type'] != 'No Record']
    df_filtered = df_filtered[df_filtered['Shift_Type_Actual'].notna()]
    shift_dist = df_filtered['Shift_Type_Actual'].value_counts().reset_index()
    shift_dist.columns = ['Shift_Type', 'Count']
    fig = px.bar(
        shift_dist,
        x='Shift_Type',
        y='Count',
        title="Distribution of Actual Shifts Worked",
        color='Count',
        color_continuous_scale='Blues'
    )
    return fig
