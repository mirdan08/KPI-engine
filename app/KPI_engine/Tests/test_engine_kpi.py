import os
import sys
sys.path.append(f"{os.getcwd()}\KPI_engine")

import unittest

import EngineCalculation.calculation_engine as calculation_engine

engine = calculation_engine.CalculationEngine()

class Testengine1(unittest.TestCase):
    
    def test_calculate(self):
        pass

if __name__ == '__main__':
    unittest.main()