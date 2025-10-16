# deviation_logic.py
import pandas as pd

# ------------------- Excel Loading & Transformation -------------------
def load_and_transform_excel(file):
    try:
        df = pd.read_excel(file, header=None)
        header_row = None
        for idx, row in df.iterrows():
            if any('STAFF' in str(cell).upper() or 'NAME' in str(cell).upper() for cell in row if pd.notna(cell)):
                header_row = idx
                break
        if header_row is None:
            return None

        date_row = header_row + 1
        day_row = header_row + 2

        dates, days = [], []
        for col_idx in range(len(df.columns)):
            cell_value = df.iloc[date_row, col_idx]
            day_value = df.iloc[day_row, col_idx] if day_row < len(df) else None
            if pd.notna(cell_value) and str(cell_value).strip().isdigit():
                dates.append(int(cell_value))
                days.append(str(day_value).strip() if pd.notna(day_value) else '')
            elif len(dates) > 0:
                dates.append(dates[-1])
                days.append(days[-1] if days else '')

        staff_col_idx = None
        for col_idx in range(len(df.columns)):
            cell = df.iloc[header_row, col_idx]
            if pd.notna(cell) and 'NAME' in str(cell).upper():
                staff_col_idx = col_idx
                break
        if staff_col_idx is None:
            staff_col_idx = 0

        data_start_row = day_row + 1
        records = []
        for row_idx in range(data_start_row, len(df)):
            staff_name = df.iloc[row_idx, staff_col_idx]
            if pd.isna(staff_name) or str(staff_name).strip() == '':
                continue
            staff_name = str(staff_name).strip()
            for col_offset, (date, day) in enumerate(zip(dates, days)):
                col_idx = staff_col_idx + 1 + col_offset
                if col_idx >= len(df.columns):
                    break
                shift_value = df.iloc[row_idx, col_idx]
                if pd.notna(shift_value):
                    shift_value = str(shift_value).strip().upper()
                    if shift_value and shift_value not in ['', 'NAN']:
                        records.append({
                            'Employee_Name': staff_name,
                            'Date': date,
                            'Day': day,
                            'Shift_Type': shift_value
                        })

        result_df = pd.DataFrame(records)
        if len(result_df) == 0:
            return None

        result_df['Employee_ID'] = result_df['Employee_Name'].apply(
            lambda x: 'EMP' + str(hash(x) % 1000).zfill(3)
        )
        return result_df
    except:
        return None

# ------------------- Shift Categorization -------------------
def get_shift_category(shift):
    shift = str(shift).upper().strip()
    if shift in ['M', 'A', 'N', 'PH']:
        return 'Working'
    elif shift in ['WO', 'NO']:
        return 'Off'
    elif shift in ['L', 'AB', 'CO']:
        return 'Leave'
    elif 'BDAY' in shift or '8AM' in shift or any(char.isdigit() for char in shift):
        return 'Special'
    else:
        return 'Other'

# ------------------- Deviation Calculation -------------------
def calculate_deviations(planned_df, actual_df):
    merged_df = pd.merge(
        planned_df[['Employee_ID', 'Employee_Name', 'Date', 'Shift_Type']],
        actual_df[['Employee_ID', 'Date', 'Shift_Type']],
        on=['Employee_ID', 'Date'],
        how='outer',
        suffixes=('_Planned', '_Actual')
    )
    name_map = pd.concat([
        planned_df[['Employee_ID', 'Employee_Name']],
        actual_df[['Employee_ID', 'Employee_Name']]
    ]).drop_duplicates('Employee_ID').set_index('Employee_ID')['Employee_Name'].to_dict()
    merged_df['Employee_Name'] = merged_df['Employee_ID'].map(name_map)
    merged_df['Planned_Category'] = merged_df['Shift_Type_Planned'].apply(get_shift_category)
    merged_df['Actual_Category'] = merged_df['Shift_Type_Actual'].apply(get_shift_category)

    def get_deviation_type(row):
        planned, actual = row['Shift_Type_Planned'], row['Shift_Type_Actual']
        planned_cat, actual_cat = row['Planned_Category'], row['Actual_Category']
        if pd.isna(planned) and pd.isna(actual):
            return 'No Record'
        if pd.notna(planned) and pd.isna(actual):
            return 'Absence' if planned_cat == 'Working' else 'No Deviation'
        if pd.isna(planned) and pd.notna(actual):
            return 'Unplanned Attendance' if actual_cat == 'Working' else 'No Deviation'
        if str(planned).upper() == str(actual).upper():
            return 'No Deviation'
        if planned_cat == 'Working' and actual_cat != 'Working':
            return 'Absence (with leave/off)'
        elif planned_cat != 'Working' and actual_cat == 'Working':
            return 'Unplanned Attendance'
        elif planned_cat == 'Working' and actual_cat == 'Working':
            return 'Shift Change'
        else:
            return 'Minor Change'

    merged_df['Deviation_Type'] = merged_df.apply(get_deviation_type, axis=1)
    merged_df['Has_Deviation'] = ~merged_df['Deviation_Type'].isin(['No Deviation', 'No Record'])
    return merged_df
