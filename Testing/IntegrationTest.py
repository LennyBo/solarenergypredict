import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
import requests
import unittest
from Tools.ApiRequest import make_request
import numpy as np
import time


    

class TestBackend(unittest.TestCase):
    def test_running(self):
        try:
            ping = make_request('http://localhost:8080/ping')
            self.assertEqual({'status': 'pong'}.items(), ping.items())
        except requests.exceptions.ConnectionError:
            raise Exception("Server not running. Please run 'python3 Backend/BackendProcess.py' before running the tests and make sure it is running in simulator mode")
        
    def test_power(self):
        heater_power = np.random.randint(500, 3000)
        twc_power = np.random.randint(500, 3000)
        house_power = np.random.randint(500, 3000)
        solar_power = np.random.randint(500, 3000)
        
        make_request(f'http://localhost:8080/simulator/setpower?heater={heater_power}&tesla={twc_power}&house={house_power}&solar={solar_power}')
        
        res = make_request('http://localhost:8080/house/power')
        self.assertEqual(res['status'], 'ok')
        self.assertIn('data', res)
        power = res['data']
        self.assertAlmostEqual(power['heater_power'], heater_power, delta=300)
        self.assertAlmostEqual(power['twc_power'], twc_power, delta=300)
        self.assertAlmostEqual(power['house_power'], house_power + twc_power + heater_power, delta=300)
        self.assertAlmostEqual(power['solar_power'], solar_power, delta=300)
        

    def test_heater_mode(self):
        heater_modes = ['Normal', 'Overdrive','Eco','Off']
        current_mode = make_request('http://localhost:8080/house/power')["data"]["heater_mode"]
        start_index = heater_modes.index(current_mode)
        for i in range(start_index,start_index + len(heater_modes),1):
            mode = heater_modes[i % len(heater_modes)]
            response = make_request(f'http://localhost:8080/house/heater?mode={mode}')
            self.assertDictEqual(response, {'status': 'ok'})
            
            time.sleep(1) # Wait for the mode to change
            
            res = make_request('http://localhost:8080/house/power')
            self.assertEqual(res['data']['heater_mode'], mode)
        
        mode = "Not a mode"
        response = make_request(f'http://localhost:8080/house/heater?mode={mode}')
        self.assertDictEqual(response, {"status": "error expected state: Overdrive, Normal, Off, Eco"})
    
        
if __name__ == '__main__':
    unittest.main()