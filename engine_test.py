import unittest

import calculation_engine
import numpy as np
engine = calculation_engine.CalculationEngine()

class TestCalculationLogic(unittest.TestCase):
    
    def test_calculate_string_operations(self):
        
        self.assertEqual(engine.calculate_KPIs("ast-xpimckaf3dlf", ("2024-10-01", "2024-10-19"), "max(cycles)"), 16720.0)
        self.assertEqual(engine.calculate_KPIs("ast-xpimckaf3dlf", ("2024-10-01", "2024-10-19"), "max(cycles - 1)"), 16719.0)
        self.assertEqual(engine.calculate_KPIs("ast-xpimckaf3dlf", ("2024-10-01", "2024-10-19"), "max(cycles + 1)"), 16721.0) 
        self.assertEqual(engine.calculate_KPIs("ast-xpimckaf3dlf", ("2024-10-01", "2024-10-19"), "max(cycles * 0)"), 0)
        self.assertEqual(engine.calculate_KPIs("ast-xpimckaf3dlf", ("2024-10-01", "2024-10-19"), "max(cycles / 2)"), None)
        
        self.assertEqual(engine.calculate_KPIs("ast-xpimckaf3dlf", ("2024-10-01", "2024-10-19"), "min(max(cycles))"), None)
        self.assertEqual(engine.calculate_KPIs("ast-xpimckaf3dlf", ("2024-10-01", "2024-10-19"), "min(min(cycles))"), None)
        self.assertEqual(engine.calculate_KPIs("ast-xpimckaf3dlf", ("2024-10-01", "2024-10-19"), "min(sum(cycles))"), None)
        self.assertEqual(engine.calculate_KPIs("ast-xpimckaf3dlf", ("2024-10-01", "2024-10-19"), "min(var(cycles))"), None)
        self.assertEqual(engine.calculate_KPIs("ast-xpimckaf3dlf", ("2024-10-01", "2024-10-19"), "min(mean(cycles))"), None)
        
        self.assertEqual(engine.calculate_KPIs("ast-xpimckaf3dlf", ("2024-10-01", "2024-10-19"), "-3 + -4"), -7)
           
           
class TestErrorOperations(unittest.TestCase):
    
    def test_division_error(self):
        self.assertEqual(engine.calculate_KPIs("ast-xpimckaf3dlf", ("2024-10-01", "2024-10-19"), "2 / 0"), None)
           

if __name__ == '__main__':
    unittest.main()