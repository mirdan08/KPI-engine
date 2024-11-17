import pandas as pd
from KPI_engine.EngineCalculation.calculation_engine import CalculationEngine
from MOCK_Knowledge_base.knowledge_base_interface import KnowledgeBaseInterface

class KPIEngine:
    def __init__(self):
        self.__calculation_engine = CalculationEngine()

    def calculate(self,
                  machine_id,
                  kpi_query,
                  operation,
                  start_time,
                  end_time
                  ):

        response = {
            "result": None,
        }
        start_datetime = None
        end_datetime = None
        try:
            start_datetime = pd.to_datetime(start_time)
            end_datetime = pd.to_datetime(end_time)
        except (TypeError, ValueError):
            response["reason"] = "invalid date format"
            response["code"] = 7
            response["result"] = None
            return response

        # query validation
        if start_datetime > end_datetime:
            response["reason"] = "start time cannot be before end time\n"
            response["code"] = 1
            response["result"] = None
            return response
        # check machine presence
        if KnowledgeBaseInterface.get_machine(machine_id) is None:
            response["reason"] = "machine not present in database\n"
            response["code"] = 2
            response["result"]=None
            return response
        
        # extract kpis involved

        calculator = CalculationEngine.Calculator(
            name="",
            description="",
            expression=kpi_query,
            KPIs=CalculationEngine._KPI_names,
            functions=CalculationEngine._base_functions
        )
        # TODO: integrate inside calculation engine (?)
        """ expr_kpis = calculator.get_KPIs()
        # check semantic validity of kpis
        if not all(
            KnowledgeBaseInterface.check_validity(machine_id, kpi, operation)
            for kpi in expr_kpis
        ):
            response["reason"] = "invalid query values"
            response["code"] = 3
            response["result"]=None
            return response """
        
        # calculate results of query
        result = calculator(
            machine_id, start_time, end_time, operation
        )
        # check result validity
        if result is None:
            response["reason"] = "wrong expression or value encountered"
            response["code"] = 5
            response["result"]=None
            return response
        elif isinstance(result, str):
            response["result"]=None
            response["reason"]="wrong values in the calculation"
            response["code"]=6
            return response
        else:
            response["result"] = result
            response["code"] = 0
        # failsafe for unseen cases
        if response["code"] != 0:
            response["reason"] = "please check parameters to be correct"
            response["code"] = 4
        return response