import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
import requests
from Tools.ApiRequest import make_request
from secret import SHELLY_IP_HEATER,SHELLY_IP_TESLA

def shelly_total_power(ip):
    try:
        return make_request(f'http://{ip}/status')['total_power']
    except requests.exceptions.ConnectionError:
        return 0
    except requests.exceptions.JSONDecodeError:
        return 0
    except KeyError:
        return 0 # We could return None for these but that will generate errors down the line


def heater_power():
    return shelly_total_power(SHELLY_IP_HEATER)

def tesla_power():
    return shelly_total_power(SHELLY_IP_TESLA)

def set_heater_switch(bits):
    bit1,bit2 = bits
    
    bit1 = 'on' if bit1 == True else 'off'
    bit2 = 'on' if bit2 == True else 'off'
    
    make_request(f'http://{SHELLY_IP_HEATER}/relay/0?turn={bit1}')
    make_request(f'http://{SHELLY_IP_TESLA}/relay/0?turn={bit2}')

def get_heater_mode():
    try:
        bit1 = make_request(f'http://{SHELLY_IP_HEATER}/relay/0')['ison']
        bit2 = make_request(f'http://{SHELLY_IP_TESLA}/relay/0')['ison']
        
        if bit1 == True and bit2 == True:
            return 'Overdrive'
        elif bit1 == True and bit2 == False:
            return 'Off'
        elif bit1 == False and bit2 == True:
            return 'Normal'
        elif bit1 == False and bit2 == False:
            return 'Eco'
        
        return (bit1,bit2)
    except requests.exceptions.ConnectionError:
        return None

def set_heater_off():
    set_heater_switch([False,True])

def set_heater_eco():
    set_heater_switch([False,False])

def set_heater_normal():
    set_heater_switch([False,True])
    
def set_heater_overdrive():
    set_heater_switch([True,True])

if __name__ == "__main__":
    set_heater_eco()
    
    

