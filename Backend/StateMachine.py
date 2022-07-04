import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
from datetime import datetime
import requests
from Tools.ApiRequest import make_request
from Tools.TeslaControl import start_charge_if_home, stop_charge_if_home


heater_on_power = 7000 # When heater is runnning, it uses about 7kw
min_tesla_on_power = 4500 # The minimum charging rate of the tesla

def get_sunrise_sunset():
    global sunrise, sunset
    try:
        data = make_request('https://api.sunrise-sunset.org/json?lat=47.0142651&lng=7.0556118&formatted=0')['results']
        sunrise = data['sunrise']
        sunset = data['sunset']
        
        sunrise = datetime.fromisoformat(sunrise[:-6])
        sunset = datetime.fromisoformat(sunset[:-6])
        
    except requests.exceptions.ConnectionError:
        print('No connection to API')
        return None, None


def control_components():
    print("Control components")
    
    is_heater_on,heater_mode, is_charging_tesla, is_tesla_home,grid_power = get_house_state()
    
    if not is_heater_on and heater_mode == 'Normal' and not is_charging_tesla: # heater off / normal / tesla not charging
        if grid_power > heater_on_power:
            heater_overdrive()
    elif not is_heater_on and heater_mode == 'Overdrive' and not is_charging_tesla: # Heater off / overdrive / tesla not charging
        if grid_power > min_tesla_on_power and is_tesla_home:
            tesla_start_charge()
        if grid_power < 6000:
            heater_normal()
    elif is_heater_on and heater_mode == 'Normal' and not is_charging_tesla: # Heater on / normal / tesla not charging
        if grid_power > min_tesla_on_power and is_tesla_home:
            tesla_start_charge()
        if grid_power > 100:
            heater_overdrive()
    elif is_heater_on and heater_mode == 'Overdrive' and not is_charging_tesla: # Heater on / overdrive / tesla not charging
        if grid_power > min_tesla_on_power and is_tesla_home:
            tesla_start_charge()
    elif not is_heater_on and heater_mode == 'Normal' and is_charging_tesla:
        if grid_power > heater_on_power:
            heater_overdrive()
        elif grid_power < -2000: # Not enough sun to charge the tesla TODO check if tesla mode is boost (meaning we overide this rule)
            tesla_stop_charge()
    elif not is_heater_on and heater_mode == 'Overdrive' and is_charging_tesla:
        if grid_power < -2000:
            tesla_stop_charge()
            heater_normal()
    elif is_heater_on and heater_mode == 'Normal' and is_charging_tesla:
        if grid_power > 1000:
            heater_overdrive()
        elif grid_power < -2000:
            tesla_stop_charge()
    elif is_heater_on and heater_mode == 'Overdrive' and is_charging_tesla:
        if grid_power < -2000:
            tesla_stop_charge()
    
        

def get_house_state():
    # Get current state of components
    data = make_request('http://localhost:8080/house/power')['data']
    heater_mode = data['heater_mode']
    is_charging_tesla = data['twc_power'] > 1000 # The tesla uses at minimum 4kw while charging
    is_heater_on = data['heater_power'] > 1000 # Heater hovers around 6kw when running
    is_tesla_home = True # Will do a request to the tesla API or maybe just the backend api that will not spam the api TODO
    grid_power = data['grid_power']
    return is_heater_on,heater_mode, is_charging_tesla, is_tesla_home,grid_power
    
    

def heater_normal():
    print('Set heater normal')
    make_request('http://localhost:8080/house/heater?mode=normal')

def heater_overdrive():
    print('Set heater overdrive')
    make_request('http://localhost:8080/house/heater?mode=overdrive')

def tesla_start_charge():
    print('Start tesla charge')
    start_charge_if_home()

def tesla_stop_charge():
    print('Stop tesla charge')
    stop_charge_if_home()
    
if __name__=="__main__":
    import time
    while True:
        control_components()
        time.sleep(5)