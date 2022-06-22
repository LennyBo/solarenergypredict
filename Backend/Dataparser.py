import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules

import numpy as np
from datetime import datetime
from Tools.Shelly import heater_power, tesla_power
from Tools.SolarEdgeModbus import CallModbus
import requests
import pandas as pd
from Tools.ApiRequest import make_request


def get_rnd_value():
    return np.random.randint(500, 3000)

class I_House_Controller:
    
    def __init__(self):
        pass
    
    def get_power(self):
        pass
    
    def get_components_state(self):
        pass
    
    def set_heater(self,state):
        pass

class Simulated_House(I_House_Controller):
    def __init__(self):
        pass
    
    def get_power(self):
        d = datetime.now().replace(second=0, microsecond=0)
        data = self.call_simulator()
        data['time'] = d.isoformat()
        # print(data)
        return data
    
    def call_simulator(self):
        return make_request('http://localhost:8081/simulator/power')['data']
    
    def set_heater(self,state):
        make_request(f'http://localhost:8081/simulator/heater/setmode?mode={state}') # TODO: Maybe add a check if the state is valid
    
            
    
    

class Real_House(I_House_Controller):
   
    def get_power(self):
            d = datetime.now().replace(second=0, microsecond=0)
            solar_edge = CallModbus()
            tesla = tesla_power()
            heater = heater_power()
            di = {
                'time':d.isoformat(),
                'solar_power': solar_edge['solar'], 
                'grid_power': solar_edge['grid'], 
                'house_power': solar_edge['house'], 
                'twc_power': tesla, 
                'heater_power': heater,
                'heater_mode': 'Overdrive', # FIXME
                'twc_mode': 'Eco' #FIXME
            }
            return di

class Random_Values(I_House_Controller):
    
    def __init__(self):
        pass
    
    def get_power():
        d = datetime.now().replace(second=0, microsecond=0)
        di = {
            'time':d.isoformat(),
            'solar_power': get_rnd_value(), 
            'grid_power': get_rnd_value(), 
            'house_power': get_rnd_value(), 
            'twc_power': get_rnd_value(), 
            'heater_power': get_rnd_value(),
            'heater_mode': 'Overdrive',
            'twc_mode': 'Eco'
        }
        return di


if __name__ == '__main__':
    dp = Simulated_House().get_power()
    