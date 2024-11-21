import pandas as pd
from os import path

DB_PATH=path.join("MOCK_Database","smart_app_data.csv")

Dataset = pd.read_csv(DB_PATH)

print(Dataset.head())

def GetValues(machine, KPI, range, operation = "avg"):

    return Dataset[(Dataset["asset_id"] == machine)
                & (Dataset["kpi"] == KPI)
                & (Dataset["time"] >= range[0])
                & (Dataset["time"] <= range[1])][operation]