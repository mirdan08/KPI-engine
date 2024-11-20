from enum import Enum
from typing import List, Optional
from pydantic import BaseModel,Field
from datetime import datetime

class AggregationOperation(Enum):
    SUM = 'sum'
    MEAN = 'mean'
    MIN = 'min'
    MAX = 'MAX'

class KPICalculationRequest(BaseModel):
    machine_id: str = Field(

    )
    operation: AggregationOperation = Field(
        default=AggregationOperation.SUM
    )
    expression: str = Field(

    ),
    start_date: datetime = Field()
    end_date: datetime = Field()