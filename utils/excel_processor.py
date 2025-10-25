import pandas as pd
import os
from utils.data_models import NurseData
from typing import Dict

def load_excel(file_path: str) -> Dict[str, NurseData]:
    """
    Load Excel file. Assumes columns: 'Nurse Name', 'Date', 'Planned', 'Actual', 'Ward' (optional).
    """
    df = pd.read_excel(file_path)
    nurses = {}
    for _, row in df.iterrows():
        name = row.get('Nurse Name')
        if pd.isna(name):
            continue
        if name not in nurses:
            nurses[name] = NurseData(name)
        nurses[name].add_record(
            date=str(row.get('Date')),
            planned=row.get('Planned', ''),
            actual=row.get('Actual', ''),
            ward=row.get('Ward') if not pd.isna(row.get('Ward')) else None
        )
    return nurses


def calculate_all_deviations(nurses: Dict[str, NurseData]) -> pd.DataFrame:
    """
    Compute deviations and return a DataFrame for output Excel.
    """
    data = []
    for nurse in nurses.values():
        deviation = nurse.calculate_deviation()
        for record in nurse.records:
            data.append({
                'Nurse Name': nurse.name,
                'Date': record['date'],
                'Planned': record['planned'],
                'Actual': record['actual'],
                'Ward': record['ward'],
                'Deviation %': deviation
            })
    return pd.DataFrame(data)


def save_excel(df: pd.DataFrame, output_path: str):
    """
    Append new data to Excel if exists; otherwise create new file.
    Also creates/updates a Summary sheet.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        try:
            existing = pd.read_excel(output_path, sheet_name="RawData")
            combined = pd.concat([existing, df], ignore_index=True)
            # Drop duplicates if same row already exists
            combined.drop_duplicates(inplace=True)
        except Exception:
            combined = df
    else:
        combined = df

    # Create summary
    summary = (
        combined.groupby(["Nurse Name", "Group", "Ward"])["Deviation %"]
        .mean()
        .reset_index()
    )

    # Always overwrite file with updated data
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        combined.to_excel(writer, sheet_name="RawData", index=False)
        summary.to_excel(writer, sheet_name="Summary", index=False)
