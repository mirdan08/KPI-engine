import pandas as pd
from calculation_engine import CalculationEngine


class KPIEngine:
    def __init__(self, db_loader, kb_loader):
        self.__db = db_loader()
        self.__kb = kb_loader()
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
        if self.__kb.get_machine(machine_id) is None:
            response["reason"] = "machine not present in database\n"
            response["code"] = 2
            response["result"]=None
            return response

        # extract kpis involved
        expr_kpis = self.__calculation_engine.extract_KPIs(
            (start_time, end_time), kpi_query
        )
        # check semantic validity of kpis
        if not all(
            self.__kb.check_validity(machine_id, kpi, operation)
            for kpi in expr_kpis
        ):
            response["reason"] = "invalid query values"
            response["code"] = 3
            response["result"]=None
            return response
        # calculate results of query
        result = self.__calculation_engine.calculate_KPIs(
            machine_id, (start_time, end_time), kpi_query
        )
        print(result)
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