from typing import Optional
from pydantic import BaseModel,Field
from datetime import datetime

class KPIRequest(BaseModel):
    class Config:
        title="KPIRequest"
        description="get the most recent KPI value by name"
    kpi_id:str=Field(
        description="kpi id"
    )
class NewKPIRequest(BaseModel):
    class Config:
        title="KPIRequest"
        description="the kpi requested"
    kpi_id:str=Field(
        description="kpi id"
    )