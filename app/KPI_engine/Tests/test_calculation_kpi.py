import os
import sys
sys.path.append(f"{os.getcwd()}\KPI_engine")

import unittest

from EngineCalculation.calculation_engine import CalculationEngine

engine = CalculationEngine

class TestCalculationLogic(unittest.TestCase):
    
    def test_getters_calculator(self):
        
        engine.add_function("fun12", "Description1", "cycles")
        engine.add_function("fun22", "Description2", "max(cycles) + 3 + fun12")
        
        fun2 = engine.get_function("fun22")
        
        self.assertEquals(fun2.get_name(), "fun22")
        self.assertEquals(fun2.get_description(), "Description2")
        self.assertEquals(fun2.get_expression(), "base_max(cycles) + 3 + fun12")
        self.assertEquals(fun2.get_KPIs(), ["cycles"])
        self.assertEquals(fun2.get_complex_functions(), ["fun12"])
        self.assertEquals(fun2.get_result_type(), float)
        
        engine.remove_function("fun12")
        engine.remove_function("fun22")

    def test_error_calculator(self):
        
        with self.assertRaises(SyntaxError):
            engine.add_function("function13", "", "cycles_ + 3")
            engine.add_function("function13", "", "cycles + 3 + function1")
        
        with self.assertRaises(TypeError):
            
            engine.add_function("function33", "", "2 < cycles")
            engine.add_function("function73", "", "fun2 / 0")
            engine.add_alert("function53", "", "2 + cycles")
            engine.add_alert("function53", "", "cycles > 0")
            engine.add_alert("function53", "", "0 > cycles")
            engine.add_alert("function53", "", "cycles > cycles")
            engine.add_alert("function73", "", "2 / 0 > 5")
        
            
    def test_add_calculator(self):    
        
        self.assertTrue(engine.add_function("function1", "", "cycles + 3"))        
        self.assertFalse(engine.add_function("function1", "", "cycles + 3"))
        self.assertTrue(engine.add_function("function2", "", "cycles + 3"))
        self.assertTrue(engine.add_function("function10", "", "cycles + 3 + function2"))

        self.assertTrue(engine.add_alert("function3", "", "2 < max(cycles)"))
        self.assertFalse(engine.add_alert("function3", "", "2 < max(cycles)"))
        self.assertTrue(engine.add_alert("function4", "", "2 < max(cycles)"))
        
    def test_get_calculator(self):
        
        self.assertTrue(type(engine.get_function("function1")), CalculationEngine.Calculator)
        self.assertTrue(type(engine.get_function("function3")), None)
        
        self.assertTrue(type(engine.get_alert("function3")), CalculationEngine.Calculator)
        self.assertTrue(type(engine.get_alert("function5")), None)
        
    def test_remove_calculator(self):
            
        self.assertTrue(engine.remove_function("function1"))
        self.assertFalse(engine.remove_function("function1"))
        self.assertFalse(engine.remove_function("function5"))
        self.assertTrue(engine.remove_function("function2"))
        self.assertTrue(engine.remove_function("function10"))
        
        self.assertFalse(engine.remove_alert("function2"))
        self.assertTrue(engine.remove_alert("function3"))
        self.assertTrue(engine.remove_alert("function4"))
    
    def test_calculate_calculator(self):

        engine.add_function("fun1", "", "max(cycles)")
        engine.add_function("fun2", "", "max(cycles - 1)")
        engine.add_function("fun3", "", "max(cycles + 1)")
        engine.add_function("fun4", "", "max(cycles * 0)")
        engine.add_function("fun5", "", "max(cycles / 2)")
        engine.add_function("fun6", "", "-3 + -4")
        engine.add_function("fun7", "", "fun2 + 2")

        self.assertEqual(engine.get_function("fun1")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19"), 16720.0)
        self.assertEqual(engine.get_function("fun2")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19"), 16719.0)
        self.assertEqual(engine.get_function("fun3")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19"), 16721.0) 
        self.assertEqual(engine.get_function("fun4")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19"), 0)
        self.assertEqual(engine.get_function("fun5")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19"), 16720 / 2)
        self.assertEqual(engine.get_function("fun6")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19"), -7)
        self.assertEqual(engine.get_function("fun7")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19"), 16721.0)
        
        engine.add_alert("fun1", "", "max(cycles) + fun6 > 0")
        self.assertEquals(engine.get_alert("fun1")("ast-xpimckaf3dlf", "2024-10-01", "2024-10-19"), True)
        engine.remove_alert("fun2")

if __name__ == "__main__":
    unittest.main()