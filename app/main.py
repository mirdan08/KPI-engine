from fastapi import Depends, FastAPI, Path, status
from fastapi.responses import JSONResponse
from KPI_engine.EngineCalculation.calculation_engine import CalculationEngine
from KPI_engine.EngineKPI.kpi_engine import KPIEngine
from models import KPI, calculation_request
app = FastAPI()

""" operation = "sum"
start_date = "2024-10-14"
end_date = "2024-10-19"
machine_id = "ast-xpimckaf3dlf"
expression = "(good_cycles/cycles)" """

engine = KPIEngine()
@app.get("/calculate/")
def calculate(
         request: calculation_request.KPICalculationRequest = Depends()
         ):
     
    code, reason, result = engine.calculate(
        request.machine_id,
        request.expression,
        request.operation,
        request.start_date,
        request.end_date
        )
    status_code = status.HTTP_200_OK
    return JSONResponse(
        content={
            'code': code.value,
            'reason': reason,
            'result': result
        },
        status_code=status_code
    )


@app.get("/KPI/{KPIID}/machineKPIValues")
def getMachineKPI(
                KPIID=Path(),
                query_params: KPI.MachineKpiValuesRequest = Depends(KPI.MachineKpiValuesRequest)
            ):
    response = {}
    status_code = status.HTTP_200_OK
    return JSONResponse(content=response, status_code=status_code)


@app.get("/KPI")
def get_kpi():
    response = {}
    status_code = status.HTTP_200_OK
    return JSONResponse(content=response, status_code=status_code)


@app.get("/KPI/{KPIName}/machines")
def get_kpi_machines(KPIName=Path()):
    response = {}
    status_code = status.HTTP_200_OK
    return JSONResponse(content=response, status_code=status_code)


@app.get("/kpi/{KPIID}")
def get_kpi_id(KPIID=Path()):
    response = {}
    status_code = status.HTTP_200_OK
    return JSONResponse(content=response, status_code=status_code)

@app.post("/KPI")
def getKPI(KPIID=Path()):
    response = {}
    status_code = status.HTTP_200_OK
    return JSONResponse(content=response, status_code=status_code)
