from enum import Enum
from KPI_engine.EngineCalculation.calculation_engine import CalculationEngine
from MOCK_Knowledge_base.knowledge_base_interface import KnowledgeBaseInterface

class KPINames(Enum):
    WORKING_TIME = "working_time"
    IDLE_TIME = "idle_time"
    OFFLINE_TIME = "offline_time"
    CONSUMPTION = "consumption"
    POWER = "power"
    COST = "cost"
    CONSUMPTION_WORKING = "consumption_working"
    CONSUMPTION_idle = "consumption_idle"
    CYCLES = "cycles"
    BAD_CYCLES = "bad_cycles"
    GOOF_CYCLES = "good_cycles"
    AVERAGE_CYCLE_TIME = "average_cycle_time"

class CalculationCodes(Enum):
    OK = 0
    INVALID_VALUES = 1
    EXPRESSION_ERROR = 2
    WRONG_DATA = 3
    GENERIC_ERROR = 4

class KPIEngine:

    def calculate(self,
                  machine_id,
                  kpi_query,
                  operation,
                  start_time,
                  end_time
                  ):

        result = None
        reason = None
        # query validation
        if start_time > end_time:
            reason = "start time cannot be before end time\n"
            code = CalculationCodes.INVALID_VALUES
            result = None
            return code, reason, result
        # check machine presence
        if KnowledgeBaseInterface.get_machine(machine_id) is None:
            reason = "machine not present in database\n"
            code = CalculationCodes.WRONG_DATA
            result = None
            return code, reason, result
        
        # extract kpis involved
        """
        calculator = CalculationEngine.Calculator(
            name="",
            description="",
            expression=kpi_query,
            KPIs=[kpi.value for kpi in KPINames],
            base_functions=CalculationEngine._base_functions_dict,
            complex_functions={},

        )
        # TODO: integrate inside calculation engine (?)
         expr_kpis = calculator.get_KPIs()
        # check semantic validity of kpis
        if not all(
            KnowledgeBaseInterface.check_validity(machine_id, kpi, operation)
            for kpi in expr_kpis
        ):
            reason = "invalid query values"
            code = 3
            result=None
            return code, reason, result 
        
        # calculate results of query
        result = calculator(
            machine_id, start_time, end_time, operation
        )
        """
        # check result validity
        if result is None:
            reason = "wrong expression or value encountered"
            code = CalculationCodes.GENERIC_ERROR
            result = None
            return code, reason, result
        elif isinstance(result, str):
            result = None
            reason = "wrong values in the calculation"
            code = CalculationCodes.GENERIC_ERROR
            return code, reason, result
        else:
            result = result
            code = CalculationCodes.OK
        # failsafe for unseen cases
        if code != CalculationCodes.OK:
            reason = "please check parameters to be correct"
            code = CalculationCodes.GENERIC_ERROR
        return code, reason, result