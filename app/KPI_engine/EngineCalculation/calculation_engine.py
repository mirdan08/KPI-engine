import os
import sys
sys.path.append(f"{os.getcwd()}")

import numpy as np
from lark import Lark, Transformer
import numexpr as ne
from py_expression_eval import Parser

from MOCK_Database.Database import GetValues as GetValuesFromDatabase
from MOCK_Knowledge_base.knowledge_base_interface import KnowledgeBaseInterface

class CalculationEngine:
    
    # column to scalar functions
    _base_functions_dict = {
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

    _other_functions_dict = dict()
    
    __alert_dict = dict()
    
    def _update_parser():
        
        KPI_names_prepare = f"/{'/ | /'.join([kpi for kpi in CalculationEngine.__KPI_names])}/"
        base_functions_dict_prepare = f"/{'/ | /'.join([base_fun for base_fun in CalculationEngine._base_functions_dict.keys()])}/"
        other_function_prepare = f"/{'/ | /'.join([fun for fun in CalculationEngine._other_functions_dict.keys()])}/"

        CalculationEngine.__parser = Lark( f"""                         
                %import common.NUMBER
                %import common.WS
                %ignore WS
                    
                ?start: l0                  -> total_base

                ?l0: l1 "<" l1              -> le
                | l1 ">" l1                 -> ge
                | l1 "=" l1                 -> eq
                | l1 "!=" l1                -> neq
                | l1 ">=" l1                -> leq
                | l1 "<=" l1                -> geq
                | l1                        -> base

                ?l1: l1 "+" l2              -> add
                | l1 "-" l2                 -> sub
                | l2                        -> base

                ?l2: l2 "*" l3              -> mul
                | l2 "/" l3                 -> div
                | l3                        -> base

                ?l3: "-" l3                 -> inverse_sign
                | kpi_name                  -> kpi
                | NUMBER                    -> number
                | base_function "(" l1 ")"  -> apply_base_function
                | other_function            -> apply_other_function
                | l3 "^" l1                 -> pow
                
                other_function:  {other_function_prepare}
                kpi_name:        {KPI_names_prepare}
                base_function:   {base_functions_dict_prepare}
                
                """,
                
            start="start")  
    
    def __check_aviable_KPIs(KPIs_list):
        return list(filter(lambda x: KnowledgeBaseInterface.get_kpi(x) != None, KPIs_list))
   
    def __check_aviable_base_functions_dict(functions_list):
        functions = [i for i in CalculationEngine._base_functions_dict.keys()]
        return list(filter(lambda x: x in functions, functions_list))
    
    def __check_aviable_other_functions(functions_list):
        functions = [i for i in CalculationEngine._other_functions_dict.keys()]
        return list(filter(lambda x: x in functions, functions_list))
 
    def __add_calculator(name, description, expression, Type):
        
        #Deviate calculus between adding function and alert situation
        if(Type == float):
            dict = CalculationEngine._other_functions_dict
            first_message = f"bool value, not a scalar or list"
            
        if(Type == bool):
            dict = CalculationEngine.__alert_dict
            first_message = f"scalar or list value, not a bool"

        if(name in dict.keys()): return False
        
        try: parsing_tree = CalculationEngine.__parser.parse(expression)
        except Exception as e: raise SyntaxError(f"Compiler is stopped here: {expression[:e.pos_in_stream+1]}<<<")
        
        #Extract the information about expression
        try: result_checking = CalculationEngine.GeneralChecking().transform(parsing_tree)
        except Exception as e: raise TypeError(e.orig_exc)
        
        if(result_checking["type"] != Type): raise TypeError(f"This expression {expression} gives a {first_message}")
        
        #Check if every KPI is aviable (and any alert is called)
        check_KPIs_aviable = CalculationEngine.__check_aviable_KPIs(result_checking["KPIs"])
        if(len(check_KPIs_aviable) != len(result_checking["KPIs"])): raise ValueError(f"The KPIs {', '.join(list(set(result_checking['KPIs']).difference(set(check_KPIs_aviable))))} are not aviables")
        
        #Check if every base function is aviable
        check_base_functions_aviable = CalculationEngine.__check_aviable_base_functions_dict(result_checking["base_functions"])
        if(len(check_base_functions_aviable) != len(result_checking["base_functions"])): raise ValueError(f"The base functions {', '.join(list(set(result_checking['base_functions']).difference(set(check_base_functions_aviable))))} are not aviables")
        
        #Check if every base function is aviable
        check_other_functions_aviable = CalculationEngine.__check_aviable_other_functions(result_checking["other_functions"])
        if(len(check_other_functions_aviable) != len(result_checking["other_functions"])): raise ValueError(f"The other functions {', '.join(list(set(result_checking['other_functions']).difference(set(check_other_functions_aviable))))} are not aviables")
        
        #Add the calculator to the dictionary
        dict[name] = CalculationEngine.Calculator(name, description, expression, result_checking["type"], check_KPIs_aviable, check_base_functions_aviable, check_other_functions_aviable)

        return True
    
    def add_function(name, description, expression):
        if(name in CalculationEngine._other_functions_dict.keys()): return False
        CalculationEngine.__add_calculator(name, description, expression, float)
        CalculationEngine._update_parser()
        return True
    
    def remove_function(name):
        if(name not in CalculationEngine._other_functions_dict.keys()): return False
        del CalculationEngine._other_functions_dict[name]
        CalculationEngine._update_parser()
        return True
    
    def get_function(name):
        
        try: return CalculationEngine._other_functions_dict[name]
        except: return None
    
    def add_alert(name, description, expression):
        return CalculationEngine.__add_calculator(name, description, expression, bool)
    
    def remove_alert(name): 
        if(name not in CalculationEngine.__alert_dict.keys()): return False
        del CalculationEngine.__alert_dict[name]  
        return True
    
    def get_alert(name):
        try: return CalculationEngine.__alert_dict[name]
        except: return None
    
    class Calculator:
        
        __calculus_parser = Parser()
        
        def __init__(self, name, description, expression, final_type, KPIs, base_functions, complex_functions):
            
            self.__name = name
            self.__description = description
            self.__expression = expression
            self.__final_type = final_type
            self.__KPIs = list(KPIs)
            self.__base_functions = base_functions
            self.__complex_functions = list(complex_functions)
            
            for base_function in self.__base_functions: self.__expression = self.__expression.replace(base_function, f"base_{base_function}")
            
            self.__base_functions = {f"base_{Function}": lambda x: CalculationEngine._base_functions_dict[Function](x) for Function in base_functions}

        def __call__(self, machine, start_date, end_date):

            KPIs = {kpi: GetValuesFromDatabase(machine, kpi, (start_date, end_date)) for kpi in self.__KPIs}
            complex_functions = {Function: CalculationEngine._other_functions_dict[Function](machine, start_date, end_date) for Function in self.__complex_functions}

            return CalculationEngine.Calculator.__calculus_parser.parse(self.__expression).evaluate(KPIs | self.__base_functions | complex_functions)

        def get_name(self):
            return self.__name
        
        def get_description(self):
            return self.__description
        
        def get_expression(self):
            return self.__expression
        
        def get_KPIs(self):
            return list(self.__KPIs)
        
        def get_complex_functions(self):
            return list(self.__complex_functions)
        
        def get_result_type(self):
            return self.__final_type
        
    #Every node pass a dict with: own type, all sub kpi name, all sub functions
    #Type float represents scalar and series (for conventional choice)
    class GeneralChecking(Transformer):
        
        def total_base(self, args):
            
            return {
                "type": float if args[0]["type"] == list else args[0]["type"],
                "KPIs": args[0]["KPIs"],
                "base_functions": args[0]["base_functions"],
                "other_functions": args[0]["other_functions"]
            }
            
        def base(self, args):
            return args[0]
        
        def __base_operation(self, args, Type):
            
            if(Type == bool and (args[0]["type"] == list or args[1]["type"] ==list)): raise TypeError("You cannot confronts with a condition a list with a scalar or a list with a list")   
            elif(Type != bool):
                if(args[0]["type"] in [float, list] and args[1]["type"] in [float, list]):
                    if(args[0]["type"] == list or args[1]["type"] == list): Type = list
                    else: Type = float
                
            return {
                "type": Type,
                "KPIs": args[0]["KPIs"] + args[1]["KPIs"],
                "base_functions": args[0]["base_functions"] + args[1]["base_functions"],
                "other_functions": args[0]["other_functions"] + args[1]["other_functions"],
                "Zero": False
            }
              
        def le(self, args):
            return self.__base_operation(args, bool)
            
        def ge(self, args):
            return self.__base_operation(args, bool)
            
        def eq(self, args):
            return self.__base_operation(args, bool)
            
        def neq(self, args):
            return self.__base_operation(args, bool)
            
        def leq(self, args):
            return self.__base_operation(args, bool)
            
        def geq(self, args):
            return self.__base_operation(args, bool)        

        def add(self, args):
            return self.__base_operation(args, float)

        def sub(self, args):
            return self.__base_operation(args, float)

        def mul(self, args):
            return self.__base_operation(args, float)

        def div(self, args):
            if(args[1]["Zero"]): raise TypeError("You cannot do a division by 0") 
            return self.__base_operation(args, float)

        def pow(self, args):
            return self.__base_operation(args, float)

        def inverse_sign(self, args):
            return args[0]

        def kpi(self, args):
            
            return {
                "type": list,
                "KPIs": [args[0].children[0].value],
                "base_functions": [],
                "other_functions": [],
                "Zero": False
            }

        def number(self, args):
            
            return {
                "type": float,
                "KPIs": [],
                "base_functions": [],
                "other_functions": [],
                "Zero": float(args[0].value) == 0
                }
                         
        def apply_base_function(self, args):
            
            return {
                "type": float,
                "KPIs": args[1]["KPIs"],
                "base_functions": args[1]["base_functions"] + [args[0].children[0].value],
                "other_functions": args[1]["other_functions"],
                "Zero": False
            }
            
        def apply_other_function(self, args):
            
            return {
                "type": CalculationEngine._other_functions_dict[args[0].children[0].value].get_result_type(),
                "KPIs": [],
                "base_functions": [],
                "other_functions": [args[0].children[0].value],
                "Zero": False
            }

CalculationEngine._update_parser()