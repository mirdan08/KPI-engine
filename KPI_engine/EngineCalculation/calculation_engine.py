import os
import sys
sys.path.append(f"{os.getcwd()}")

import numpy as np
from lark import Lark, Transformer

from MOCK_Database.Database import GetValues as GetValuesFromDatabase

class CalculationEngine:
    # column to scalar functions
    _base_functions = {
        "max": lambda x: max(x),
        "min": lambda x: min(x),
        "sum": lambda x: sum(x),
        "mean": lambda x: np.mean(x),
        "var": lambda x: np.var(x),
    }

    __KPI_names = [
        "working_time",
        "idle_time",
        "offline_time",
        "consumption",
        "power",
        "cost",
        "consumption_working",
        "consumption_idle",
        "cycles",
        "bad_cycles",
        "good_cycles",
        "average_cycle_time"
    ]

    # basic functions and names parsing
    __KPI_names_prepare = f"/{'/ | /'.join([kpi for kpi in __KPI_names])}/"

    __base_functions_prepare = (
        f"/{'/ | /'.join([kpi for kpi in _base_functions.keys()])}/"
    )

    __parser = Lark(
        f"""
            ?start: l1

            ?l1: l1 "+" l2             -> add
               | l1 "-" l2             -> sub
               | l2                    
           
            ?l2: l2 "*" l3             -> mul
               | l2 "/" l3             -> div
               | l3                    
           
            ?l3: "-" l3                -> inverse_sign
               | kpi_name              -> kpi
               | NUMBER                -> number
               | function "(" l1 ")"   -> apply_function
               | [l1] "(" l1 ")" [l1]  -> brackets
               | l3 "^" l1             -> pow
               
            kpi_name: {__KPI_names_prepare}
            function: {__base_functions_prepare}
            
            %import common.NUMBER
            %import common.WS
            %ignore WS
            """,
        start="start",
    )

    # mock call to a real db 
    def _call_KPI(machine, KPI, range, operation="sum"):
        return GetValuesFromDatabase(machine, KPI, range, operation)

    def extract_KPIs(machine, range, string_expression):
        try:
            exp_parser = CalculationEngine.CalculateExpressionTree(
                machine,
                range
                )
            exp_parser.transform(
                CalculationEngine.__parser.parse(string_expression)
                )
            return exp_parser.get_expression_kpis()
        except Exception as e:
            return set()

    def calculate_KPIs(self, machine, range, string_expression):
        # calculate expression value
        try:
            exp_parser = CalculationEngine.CalculateExpressionTree(machine, range)
            result = exp_parser.transform(
                CalculationEngine.__parser.parse(string_expression)
            )
        except Exception as e:
            return None

        # handle series of values errors
        try:
            if np.isnan(result).any(): return "some values are missing"
            if np.isinf(result).any(): return "error during calculations of the series"
                
        # handle scalar values errors
        except:
            if np.isnan(result): return "missing value"
            if np.isinf(result): return "error during calculation of values value"
              
        # no nan or inf values -> return result
        return result

    class CalculateExpressionTree(Transformer):

        def __init__(self, machine, range):
            self.__machine = machine
            self.__range = range
            self.__expr_kpis = set()

        def get_expression_kpis(self):
            return self.__expr_kpis

        def add(self, args):
            return args[0] + args[1]

        def sub(self, args):
            return args[0] - args[1]

        def mul(self, args):
            return args[0] * args[1]

        def div(self, args):
            if (args[1]==0).any(): return np.inf
            return args[0] / args[1]

        def pow(self, args):
            return args[0] ** args[1]

        def brackets(self, args):

            result = args[1]

            if args[0] is not None:
                result *= args[0]
            if args[2] is not None:
                result *= args[2]

            return result

        def inverse_sign(self, args):
            return -args[0]

        def kpi(self, args):
            
            self.__expr_kpis.add(args[0].children[0].value)
            result = CalculationEngine._call_KPI(
                self.__machine, args[0].children[0].value, self.__range
                ).to_numpy()
            return result

        def number(self, args):
            return float(args[0])

        def apply_function(self, args):
            return CalculationEngine._base_functions[args[0].children[0].value](args[1])

