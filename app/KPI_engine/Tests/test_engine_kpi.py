import os
import sys
sys.path.append(f"{os.getcwd()}\KPI_engine")

import unittest

import EngineCalculation.calculation_engine as calculation_engine

engine = calculation_engine.CalculationEngine()

class Testengine1(unittest.TestCase):
    
    def test_method1(self):
        pass
           
class TestEngine2(unittest.TestCase):
    
    def test_method2(self):
        self.assertEqual(engine.calculate_KPIs("ast-xpimckaf3dlf", ("2024-10-01", "2024-10-19"), "2 / 0"), None)
           

if __name__ == '__main__':
    unittest.main()