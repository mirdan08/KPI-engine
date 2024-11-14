import pandas as pd

Dataset = pd.read_csv("MOCK_Database\smart_app_data.csv")

def GetValues(machine, KPI, range, operation):

    return Dataset[(Dataset["asset_id"] == machine)
                & (Dataset["kpi"] == KPI)
                & (Dataset["time"] >= range[0])
                & (Dataset["time"] <= range[1])][operation]