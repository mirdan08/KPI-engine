import os
import sys
import numpy as np
import numexpr as ne

from lark import Lark, Transformer
from py_expression_eval import Parser

from MOCK_Database.Database import GetValues as GetValuesFromDatabase
from MOCK_Knowledge_base.knowledge_base_interface import KnowledgeBaseInterface

sys.path.append(f"{os.getcwd()}")

class CalculationEngine:
    
    # column to scalar functions
    _base_functions = {
        "max": lambda x: max(x),
        "min": lambda x: min(x),
        "sum": lambda x: sum(x),
        "mean": lambda x: np.mean(x),
        "var": lambda x: np.var(x),
    }

    _KPI_names = [
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
    __KPI_names_prepare = f"/{'/ | /'.join([kpi for kpi in _KPI_names])}/"

    __base_functions_prepare = (
        f"/{'/ | /'.join([kpi for kpi in _base_functions.keys()])}/"
    )

    __parser = Lark(
        f"""
            ?start: l0
            
            ?l0: l1 "<" l1             -> le
               | l1 ">" l1             -> ge
               | l1 "=" l1             -> eq
               | l1 "!=" l1            -> neq
               | l1 ">=" l1            -> leq
               | l1 "<=" l1            -> geq

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
    
    __function_dict = dict()
    
    __alert_dict = dict()
    
    def __check_aviable_KPIs(self, KPIs_list):
        return list(filter(lambda x: KnowledgeBaseInterface.get_kpi(x) != None, KPIs_list))
   
    def __check_aviable_functions(self, functions_list):
        functions = list(CalculationEngine._base_function.keys()) + (CalculationEngine.__function_dict.keys())
        return list(filter(lambda x: x in functions, functions_list))
 
    def __parsing_phase(expression):
        return CalculationEngine.__parser.parse(expression)
    
    def __add_calculator(name, description, expression, Type):
        
        #Deviate calculus between adding function and alert situation
        if(Type == float):
            dict = CalculationEngine.__function_dict
            first_message = f"bool value, not a scalar or list"
            
        if(Type == bool):
            dict = CalculationEngine.__alert_dict
            first_message = f"scalar or list value, not a bool"

        if(name in dict.keys()): return False 
        
        #Extract the information about expression
        result_checking = CalculationEngine.__parsing_phase(expression)
        if(result_checking["type"] != Type): raise TypeError(f"This expression {expression} gives a {first_message}")
        
        #Check if every KPI is aviable (and any alert is called)
        check_KPIs_aviable = CalculationEngine.__check_aviable_KPIs(result_checking['KPIs'])
        if(len(check_KPIs_aviable) != len(result_checking['KPIs'])): raise ValueError(f"The KPIs {', '.join(list(set(result_checking['KPIs']).difference(set(check_KPIs_aviable))))}are not aviables")
        
        #Check if every function is aviable
        check_functions_aviable = CalculationEngine.__check_aviable_functions(result_checking["functions"])
        if(len(check_functions_aviable) != len(result_checking["functions"])): raise ValueError(f"The functions {', '.join(list(set(result_checking['functions']).difference(set(check_functions_aviable))))} are not aviables")
        
        #Add the calculator to the dictionary
        dict[name] = CalculationEngine.Function(name, description, expression, check_KPIs_aviable, check_functions_aviable)
        
        return True
    
    def add_function(name, description, expression):
        return CalculationEngine.__add_calculator(name, description, expression, float)
    
    def remove_function(name):
        
        if(name not in CalculationEngine.__function_dict.keys()): return False
        del CalculationEngine.__function_dict[name]
        
        return True
    
    def get_function(name):
        return CalculationEngine.__function_dict[name]
    
    def add_alert(name, description, expression):
        return CalculationEngine.__add_calculator(name, description, expression, bool)
    
    def remove_alert(name):
        
        if(name not in CalculationEngine.__alert_dict.keys()): return False
        del CalculationEngine.__alert_dict[name]
        
        return True
    
    def get_alert(name):
        return CalculationEngine.__alert_dict[name]
    
    class Calculator:
        
        __calculus_parser = Parser()
        
        def __init__(self, name, description, expression, KPIs, functions):
            
            self.__name = name
            self.__description = description
            self.__expression = expression
            self.__KPIs = list(KPIs)
            self.__functions = list(functions)
         
        def __call__(self, machine, start_date, end_date,operation):
            
            KPIs_dict = {kpi: GetValuesFromDatabase(machine, kpi, (start_date, end_date),operation) for kpi in self.__KPIs}
            total_functions = self.__functions | CalculationEngine._base_functions
            
            return CalculationEngine.Calculator.__calculus_parser.parse(self.__expression).evaluate({Function: lambda x: total_functions[Function](x) for Function in total_functions.keys()} | KPIs_dict)

        def get_name(self):
            return self.__name
        
        def get_description(self):
            return self.__description
        
        def get_expression(self):
            return self.__expression
        
        def get_KPIs(self):
            return list(self.__KPIs)
        
        def get_functions(self):
            return list(self.__functions)
        
    #Every node pass a dict with: own type, all sub kpi name, error
    #Type float represents scalar and series (for conventional choice)
    class GeneralChecking(Transformer):
        
        def le(self, args):
            
            return {
                "type": bool,
                "KPIs": args[0]["KPIs"] + args[1]["KPIs"],
                "functions": args[0]["functions"] + args[1]["functions"]
            }
            
        def ge(self, args):
            
            return {
                "type": bool,
                "KPIs": args[0]["KPIs"] + args[1]["KPIs"],
                "functions": args[0]["functions"] + args[1]["functions"]
            }
            
        def eq(self, args):
            
            return {
                "type": bool,
                "KPIs": args[0]["KPIs"] + args[1]["KPIs"],
                "functions": args[0]["functions"] + args[1]["functions"]
            }
            
        def neq(self, args):
            
            return {
                "type": bool,
                "KPIs": args[0]["KPIs"] + args[1]["KPIs"],
                "functions": args[0]["functions"] + args[1]["functions"]
            }
            
        def leq(self, args):
            
            return {
                "type": bool,
                "KPIs": args[0]["KPIs"] + args[1]["KPIs"],
                "functions": args[0]["functions"] + args[1]["functions"]
            }
            
        def geq(self, args):
            
            return {
                "type": bool,
                "KPIs": args[0]["KPIs"] + args[1]["KPIs"],
                "functions": args[0]["functions"] + args[1]["functions"]
            }         

        def add(self, args):
            
            return {
                "type": float,
                "KPIs": args[0]["KPIs"] + args[1]["KPIs"],
                "functions": args[0]["functions"] + args[1]["functions"]
            }

        def sub(self, args):
            
            return {
                "type": float,
                "KPIs": args[0]["KPIs"] + args[1]["KPIs"],
                "functions": args[0]["functions"] + args[1]["functions"]
            }

        def mul(self, args):
            
            return {
                "type": float,
                "KPIs": args[0]["KPIs"] + args[1]["KPIs"],
                "functions": args[0]["functions"] + args[1]["functions"]
            }

        def div(self, args):
            
            return {
                "type": float,
                "KPIs": args[0]["KPIs"] + args[1]["KPIs"],
                "functions": args[0]["functions"] + args[1]["functions"]
            }

        def pow(self, args):
            
            return {
                "type": float,
                "KPIs": args[0]["KPIs"] + args[1]["KPIs"],
                "functions": args[0]["functions"] + args[1]["functions"]
            }

        def brackets(self, args):
            
            KPIs = []
            functions = []
            
            for arg in args:
                KPIs += arg["KPIs"]
                functions += arg["functions"]
                    
            return  {
                "type": float,
                "KPIs": KPIs,
                "functions": functions
            }

        def inverse_sign(self, args):
            return args[0]

        def kpi(self, args):
            
            return {
                "type": float,
                "KPIs": [args[0].children[0].value],
                "functions": []
            }

        def number(self, args):
            
            return {
                "type": float,
                "KPIs": [],
                "functions": []
                }
                         
        def apply_function(self, args):
            
            return {
                "type": args[0]["type"],
                "KPIs": args[0]["KPIs"],
                "functions": args[0]["functions"] + [args[0].value]
            }