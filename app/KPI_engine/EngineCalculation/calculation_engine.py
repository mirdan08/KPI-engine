import os
import sys
sys.path.append(f"{os.getcwd()}\\app")

import numpy as np
from lark import Lark, Transformer
import numexpr as ne
from py_expression_eval import Parser

from MOCK_Database.Database_interface import GetValues as GetValuesFromDatabase
from MOCK_Database.Database_interface import GetTimeRange as GetTimeRangeFromDatabase
from MOCK_Knowledge_base.knowledge_base_interface import KnowledgeBaseInterface

class CalculationEngine:

    #Dictionary of all base functions
    _base_functions_dict = {
        "max": lambda x: max(x),
        "min": lambda x: min(x),
        "sum": lambda x: sum(x),
        "avg": lambda x: np.mean(x),
        "var": lambda x: np.var(x),
    }

    _complex_KPIs_dict = dict()  #Dict of all complex KPIs created
    __alert_dict = dict()        #Dict of all alerts created
    
    _total_calculators = dict()    #Dict of all calculators
    
    #Update parsing (for everytime some alert or complex KPIs are added or removed)
    def _update_parser():
        
        #Update total calculators
        CalculationEngine._total_calculators = CalculationEngine._complex_KPIs_dict | CalculationEngine.__alert_dict
        
        #Prepare string for parser
        base_functions_dict_prepare = f"/{'/ | /'.join([base_fun for base_fun in CalculationEngine._base_functions_dict.keys()])}/"
        calculators_prepare = f"/{'/ | /'.join([fun for fun in CalculationEngine._total_calculators.keys()])}/"
        
        #Updare parser
        CalculationEngine.__parser = Lark( f"""                         
                %import common.NUMBER
                %import common.WS
                %ignore WS
                    
                ?start: l0                  -> base

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
                | base_function "(" l1 ")"  -> apply_base_function
                | l3 "^" l1                 -> pow
                | calculators               -> apply_calculators
                | kpi_name                  -> kpi
                | NUMBER                    -> number 
                
                base_function:   {base_functions_dict_prepare}
                kpi_name:        /[a-z_]+/
                calculators:       {calculators_prepare}
                
                """,
                
            start="start")
    
    #Filter aviable base KPI names
    def __filter_aviable_KPIs(KPIs_list):
        return list(filter(lambda x: KnowledgeBaseInterface.get_kpi(x) != None, KPIs_list))
    
    #Filter aviable base function names
    def __filter_aviable_base_functions_dict(base_functions_list):
        base_functions = [i for i in CalculationEngine._base_functions_dict.keys()]
        return list(filter(lambda x: x in base_functions, base_functions_list))
    
    #Filter aviable calculator names
    def __filter_aviable_complex_KPIs(calculators_list):
        calculators = [i for i in CalculationEngine._total_calculators.keys()]
        return list(filter(lambda x: x in calculators, calculators_list))
    
    #Get a new creation
    def __get_new_creation(name, description, expression, Type):
        
        #Deviate calculus between adding function and alert situation
        if(float in Type and list in Type):
            dict = CalculationEngine._complex_KPIs_dict
            first_message = f"bool value, not a scalar or list"
            
        if(bool in Type):
            dict = CalculationEngine.__alert_dict
            first_message = f"scalar or list value, not a bool"
        
        #Compile
        try: parsing_tree = CalculationEngine.__parser.parse(expression)
        except Exception as e: raise SyntaxError(f"Compiler is stopped here: {expression[:e.pos_in_stream+1]}<<<")
        
        #Extract the information about expression
        try: result_checking = CalculationEngine.GeneralChecking().transform(parsing_tree)
        except Exception as e: raise TypeError(e.orig_exc)
        
        #Check if type of expression is equals to excepted type
        if(result_checking["type"] not in Type): raise TypeError(f"This expression {expression} gives a {first_message}")
        
        #Check if this calculator doesn't call itself
        if(name in result_checking["calculators"]): raise ValueError(f"This creation cannot call itself")
        
        #Check if every base KPI is aviable
        check_KPIs_aviable = CalculationEngine.__filter_aviable_KPIs(result_checking["KPIs"])
        if(len(check_KPIs_aviable) != len(result_checking["KPIs"])): raise SyntaxError(f"The simply KPIs {', '.join(list(set(result_checking['KPIs']).difference(set(check_KPIs_aviable))))} are not aviables")
        
        #Check if every base function is aviable
        check_base_functions_aviable = CalculationEngine.__filter_aviable_base_functions_dict(result_checking["base_functions"])
        if(len(check_base_functions_aviable) != len(result_checking["base_functions"])): raise ValueError(f"The base functions {', '.join(list(set(result_checking['base_functions']).difference(set(check_base_functions_aviable))))} are not aviables")
        
        #Check if every complex KPI is aviable
        check_complex_KPIs_aviable = CalculationEngine.__filter_aviable_complex_KPIs(result_checking["calculators"])
        if(len(check_complex_KPIs_aviable) != len(result_checking["calculators"])): raise ValueError(f"The complex KPIs {', '.join(list(set(result_checking['calculators']).difference(set(check_complex_KPIs_aviable))))} are not aviables")
        
        return dict, CalculationEngine.Calculator(name, description, expression, result_checking["type"], check_KPIs_aviable, check_base_functions_aviable, check_complex_KPIs_aviable)
        
    #Add calculator
    def __add_calculator(name, description, expression, Type):
        
        #Deviate calculus between adding function and alert situation
        if(float in Type and list in Type and name in CalculationEngine._complex_KPIs_dict.keys() or
           bool in Type and name in CalculationEngine.__alert_dict.keys()): return False
        
        name_dict, Creation = CalculationEngine.__get_new_creation(name, description, expression, Type)
        
        #Add the calculator to the dictionary
        name_dict[name] = Creation
        
        return True
    
    def direct_calculation_KPI(machine, formula, start_date, end_date):
        return CalculationEngine.__get_new_creation("", "", formula, [float, list])[1](machine, start_date, end_date)
    
    def direct_calculation_alert(machine, formula, start_date, end_date):
        return CalculationEngine.__get_new_creation("", "", formula, [bool])[1](machine, start_date, end_date)
    
    def add_complex_KPI(name, description, expression):
        if(name in CalculationEngine._complex_KPIs_dict.keys()): return False
        CalculationEngine.__add_calculator(name, description, expression, [float, list])
        CalculationEngine._update_parser()
        return True
    
    def remove_complex_KPI(name):
        if(name not in CalculationEngine._complex_KPIs_dict.keys()): return False
        del CalculationEngine._complex_KPIs_dict[name]
        CalculationEngine._update_parser()
        return True
    
    def get_complex_KPI(name):
        try: return CalculationEngine._complex_KPIs_dict[name]
        except: return None
    
    def add_alert(name, description, expression):
        return CalculationEngine.__add_calculator(name, description, expression, [bool])
    
    def remove_alert(name): 
        if(name not in CalculationEngine.__alert_dict.keys()): return False
        del CalculationEngine.__alert_dict[name]  
        return True
    
    def get_alert(name):
        try: return CalculationEngine.__alert_dict[name]
        except: return None
        
    def get_alert_names():
        return [i for i in CalculationEngine.__alert_dict.keys()]
    
    def get_complex_KPI_names():
        return [i for i in CalculationEngine._complex_KPIs_dict.keys()]
    
    class Calculator:
        
        __calculus_parser = Parser()
        
        def __init__(self, name, description, expression, final_type, KPIs, base_functions, complex_KPIs):
            
            self.__name = name
            self.__description = description
            self.__expression = expression
            self.__final_type = final_type
            self.__KPIs = list(KPIs)
            self.__complex_KPIs = list(complex_KPIs)

            for base_function in base_functions: self.__expression = self.__expression.replace(base_function, f"base_{base_function}")
            
            self.__base_functions = {f"base_{Function}": lambda x: CalculationEngine._base_functions_dict[Function](x) for Function in base_functions}
            
        def __call__(self, machine, start_date, end_date):

            KPIs = {kpi: GetValuesFromDatabase(machine, kpi, (start_date, end_date)) for kpi in self.__KPIs}
            complex_KPIs = {Function: CalculationEngine._complex_KPIs_dict[Function](machine, start_date, end_date)["values"] for Function in self.__complex_KPIs}
            
            Calculation = CalculationEngine.Calculator.__calculus_parser.parse(self.__expression).evaluate(KPIs | complex_KPIs | self.__base_functions)
            
            return {
                "time": None if type(Calculation) != np.ndarray else GetTimeRangeFromDatabase(start_date, end_date),
                "values": Calculation
            }

        def get_name(self):
            return self.__name
        
        def get_description(self):
            return self.__description
        
        def get_expression(self):
            return self.__expression
        
        def get_KPIs(self):
            return list(self.__KPIs)
        
        def get_complex_KPIs(self):
            return list(self.__complex_KPIs)
        
        def get_result_type(self):
            return self.__final_type
        
    #Every node pass a dict with: own type, all sub kpi name, all sub functions
    #Type float represents scalar and series (for conventional choice)
    class GeneralChecking(Transformer):

        def base(self, args):
            return args[0]
        
        def __base_operation(self, args, Type):
 
            return {
                "type": Type,
                "KPIs": args[0]["KPIs"] + args[1]["KPIs"],
                "base_functions": args[0]["base_functions"] + args[1]["base_functions"],
                "calculators": args[0]["calculators"] + args[1]["calculators"],
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
                "calculators": [],
                "Zero": False
            }

        def number(self, args):
            
            return {
                "type": float,
                "KPIs": [],
                "base_functions": [],
                "calculators": [],
                "Zero": float(args[0].value) == 0
                }
                         
        def apply_base_function(self, args):
            
            return {
                "type": float,
                "KPIs": args[1]["KPIs"],
                "base_functions": args[1]["base_functions"] + [args[0].children[0].value],
                "calculators": args[1]["calculators"],
                "Zero": False
            }
            
        def apply_calculators(self, args):
            
            return {
                "type": CalculationEngine._complex_KPIs_dict[args[0].children[0].value].get_result_type(),
                "KPIs": [],
                "base_functions": [],
                "calculators": [args[0].children[0].value],
                "Zero": False
            }

CalculationEngine._update_parser()