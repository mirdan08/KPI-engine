from fastapi import FastAPI
from KPI_engine.EngineKPI.kpi_engine import KPIEngine

app = FastAPI()

""" operation = "sum"
start_date = "2024-10-14"
end_date = "2024-10-19"
machine_id = "ast-xpimckaf3dlf"
expression = "(good_cycles/cycles)" """


@app.get("/calculate/")
def calculate(
         machine_id: str = None,
         operation: str = "sum",
         expression: str = None,
         start_date: str = None,
         end_date: str = None
         ):
     engine = KPIEngine()
     return engine.calculate(machine_id,
                            expression,
                            operation,
                            start_date,
                            end_date
                            )