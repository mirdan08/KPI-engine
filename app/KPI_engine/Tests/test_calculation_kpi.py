import os
import sys
sys.path.append(f"{os.getcwd()}\\app\\KPI_engine")

import numpy as np

import unittest

from EngineCalculation.calculation_engine import CalculationEngine

engine = CalculationEngine

class TestCalculationLogic(unittest.TestCase):
    
    def test_getters_calculator(self):
        
        engine.add_complex_KPI("fun12", "Description1", "cycles")
        engine.add_complex_KPI("fun22", "Description2", "max(cycles) + 3 + fun12")
        
        fun2 = engine.get_complex_KPI("fun22")
        
        self.assertEquals(fun2.get_name(), "fun22")
        self.assertEquals(fun2.get_description(), "Description2")
        self.assertEquals(fun2.get_expression(), "base_max(cycles) + 3 + fun12")
        self.assertEquals(fun2.get_KPIs(), ["cycles"])
        self.assertEquals(fun2.get_complex_KPIs(), ["fun12"])
        self.assertEquals(fun2.get_result_type(), float)
        
        engine.remove_complex_KPI("fun12")
        engine.remove_complex_KPI("fun22")

    def test_error_calculator(self):
        
        with self.assertRaises(SyntaxError):
            engine.add_complex_KPI("function13", "", "cycles_ + 3")
            engine.add_complex_KPI("function13", "", "cycles + 3 + function1")
            
            engine.add_complex_KPI("function93", "", "function93 + 3")
            engine.add_alert("function93", "", "function93 > 0")
        
        with self.assertRaises(TypeError): 
            engine.add_complex_KPI("function33", "", "2 < cycles")
            
        with self.assertRaises(TypeError): 
            engine.add_complex_KPI("function73", "", "fun2 / 0")
        
        with self.assertRaises(TypeError): 
            engine.add_alert("function53", "", "2 + cycles")
            
        with self.assertRaises(TypeError): 
            engine.add_alert("function73", "", "2 / 0 > 5")
        
            #Base function are not aviable
            #Other function are not aviable
                
    def test_add_calculator(self):    
        
        self.assertTrue(engine.add_complex_KPI("function1", "", "cycles + 3"))        
        self.assertFalse(engine.add_complex_KPI("function1", "", "cycles + 3"))
        self.assertTrue(engine.add_complex_KPI("function2", "", "cycles + 3"))
        self.assertTrue(engine.add_complex_KPI("function10", "", "cycles + 3 + function2"))

        self.assertTrue(engine.add_alert("function3", "", "2 < max(cycles)"))
        self.assertFalse(engine.add_alert("function3", "", "2 < max(cycles)"))
        self.assertTrue(engine.add_alert("function4", "", "2 < max(cycles)"))
        
    def test_get_calculator(self):
        
        self.assertTrue(type(engine.get_complex_KPI("function1")), CalculationEngine.Calculator)
        self.assertTrue(type(engine.get_complex_KPI("function3")), None)
        
        self.assertTrue(type(engine.get_alert("function3")), CalculationEngine.Calculator)
        self.assertTrue(type(engine.get_alert("function5")), None)
        
    def test_remove_calculator(self):
            
        self.assertTrue(engine.remove_complex_KPI("function1"))
        self.assertFalse(engine.remove_complex_KPI("function1"))
        self.assertFalse(engine.remove_complex_KPI("function5"))
        self.assertTrue(engine.remove_complex_KPI("function2"))
        self.assertTrue(engine.remove_complex_KPI("function10"))
        
        self.assertFalse(engine.remove_alert("function2"))
        self.assertTrue(engine.remove_alert("function3"))
        self.assertTrue(engine.remove_alert("function4"))
    
    def test_calculate_calculator(self):

        engine.add_complex_KPI("fun1", "", "max(cycles)")
        engine.add_complex_KPI("fun2", "", "max(cycles - 1)")
        engine.add_complex_KPI("fun3", "", "max(cycles + 1)")
        engine.add_complex_KPI("fun4", "", "max(cycles * 0)")
        engine.add_complex_KPI("fun5", "", "max(cycles / 2)")
        engine.add_complex_KPI("fun6", "", "-3 + -4")
        engine.add_complex_KPI("fun7", "", "fun2 + 2")
        
        self.assertEqual(engine.get_complex_KPI("fun1")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19")["values"], 16720.0)
        self.assertEqual(engine.get_complex_KPI("fun2")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19")["values"], 16719.0)
        self.assertEqual(engine.get_complex_KPI("fun3")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19")["values"], 16721.0) 
        self.assertEqual(engine.get_complex_KPI("fun4")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19")["values"], 0)
        self.assertEqual(engine.get_complex_KPI("fun5")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19")["values"], 16720 / 2)
        self.assertEqual(engine.get_complex_KPI("fun6")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19")["values"], -7)
        self.assertEqual(engine.get_complex_KPI("fun7")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19")["values"], 16721.0)
        
        engine.add_alert("fun1", "", "max(cycles) + fun6 > 0")
        self.assertEquals(engine.get_alert("fun1")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19")["values"], True)
        engine.remove_alert("fun2")
        
        engine.add_complex_KPI("fun8", "", "cycles + 2")
        
    def test_type_result(self):
        
        engine.add_complex_KPI("fun991", "", "cycles")
        engine.add_complex_KPI("fun992", "", "max(cycles)")
        engine.add_alert("fun991", "", "cycles > 0")
        
        Result1 = engine.get_complex_KPI("fun991")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19")
        Result2 = engine.get_complex_KPI("fun992")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19")
        Result3 = engine.get_alert("fun991")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19")
        
        self.assertIsInstance(Result1["time"], np.ndarray)
        self.assertEqual(Result2["time"], None)
        self.assertIsInstance(Result3["time"], np.ndarray)
        
        self.assertIsInstance(Result1["values"], np.ndarray)
        self.assertIsInstance(Result2["values"], float)
        self.assertIsInstance(Result3["values"], np.ndarray)
        
        print(Result1)
        print("")
        print(Result2)
        print("")
        print(Result3)
        

if __name__ == "__main__":
    unittest.main()