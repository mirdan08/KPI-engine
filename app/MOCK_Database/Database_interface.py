import pandas as pd
from os import path

Dataset = pd.read_csv(path.join("app", "MOCK_Database", "smart_app_data.csv"))

def GetValues(machine, KPI, range, operation = "sum"):

    return Dataset[(Dataset["asset_id"] == machine)
                & (Dataset["kpi"] == KPI)
                & (Dataset["time"] >= range[0])
                & (Dataset["time"] <= range[1])][operation]
    
def GetTimeRange(start_time, end_time):
    return list(set(Dataset[(Dataset["time"] >= start_time) & (Dataset["time"] <= end_time)]["time"]))