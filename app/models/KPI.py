from typing import List, Optional
from pydantic import BaseModel,Field
from datetime import datetime


class MachineKpiValuesRequest(BaseModel):
    class Config:
        title="MachineKPIValuesRequest"
        description="A model for requesting kpi calculations on machines"
    KPIID:str=Field(
        description="KPI id"
        )
    machines:Optional[str] = Field(
        description="list of the requested machines",
        default=None
        )
    startDate:Optional[datetime] = Field(
        description="start datetime of the requeste period",
        default=None
        )
    endDate:Optional[datetime]=Field(
        description="end datetime of the requested period",
        default=None
        )
class KPIRequest(BaseModel):
    class Config:
        title="KPIRequest"
        description="A model for KPI requests"
class KPIMachinesRequest(BaseModel):
    class Config:
        title="KPIMachinesRequest"
    KPIName:str=Field(
        description="Name of the KPI"
    )