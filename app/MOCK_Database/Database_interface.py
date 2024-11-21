import numpy as np
import pandas as pd
import os
import sys
sys.path.append(f"{os.getcwd()}\\app\\MOCK_Database")

from os import path

Dataset = pd.read_csv(path.join("app", "MOCK_Database", "smart_app_data.csv"))

def GetValues(machine, KPI, range, operation = "sum"):

    return Dataset[(Dataset["asset_id"] == machine) &
                             (Dataset["kpi"] == KPI) &
                             (Dataset["time"] >= range[0]) &
                             (Dataset["time"] <= range[1])][operation].to_numpy()
    
def GetTimeRange(start_time, end_time):
    return np.array(set(Dataset[(Dataset["time"] >= start_time) & (Dataset["time"] <= end_time)]["time"]))