import os
import sys
import unittest
from fastapi.testclient import TestClient
from main import app

sys.path.append(f"{os.getcwd()}\KPI_engine")

client = TestClient(app)

class TestApi(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    def test_api_response(self):
        response = self.client.get("localhost:8000/calculate/?machine_id=ast-xpimckaf3dlf&expression=(good_cycles/cycles)&start_date=2024-10-14&end_date=2024-10-19")
        self.assertEqual(response.status_code,200)