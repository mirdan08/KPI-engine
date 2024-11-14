from os import path

from MOCK_Knowledge_base.KB import get_KB
from MOCK_Knowledge_base.knowledge_base import KnowledgeBase
from KPI_engine.EngineKPI.kpi_engine import KPIEngine
import pandas as pd


def db_loader():
    DB_URL = path.join(".", "smart_app_data.csv")
    db = pd.read_csv(DB_URL)
    db["time"] = pd.to_datetime(db["time"])
    return db


def kb_loader():
    return KnowledgeBase(get_KB())


engine = KPIEngine(
    db_loader=db_loader,
    kb_loader=kb_loader
)
operation = "sum"
start_date = "2024-10-14"
end_date = "2024-10-19"
machine_id = "ast-xpimckaf3dlf"
expression = "(good_cycles/cycles)"
print(
    f"""
Calculating operation {operation} on {expression} from {start_date} to {end_date} on machine with id {machine_id}:\n
result={engine.calculate(machine_id, expression, operation, start_date, end_date)}
"""
)