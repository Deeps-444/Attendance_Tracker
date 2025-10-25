
from typing import Dict, List

class NurseData:
    def __init__(self, name: str):
        self.name = name
        self.records: List[Dict] = []  # List of dicts: {'date': str, 'planned': str, 'actual': str, 'ward': str or None}

    def add_record(self, date: str, planned: str, actual: str, ward: str = None):
        self.records.append({'date': date, 'planned': planned, 'actual': actual, 'ward': ward})

    def calculate_deviation(self) -> float:
        if not self.records:
            return 0.0
        deviated_days = sum(1 for r in self.records if r['planned'] != r['actual'])
        return (deviated_days / len(self.records)) * 100