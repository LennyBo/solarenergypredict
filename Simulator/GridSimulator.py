import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
from bottle import request, get
from datetime import datetime, date
from Backend.DatabaseModule import database as db
import json
import numpy as np

def get_heater_power():
    return heater_power + np.random.normal(0,100)

def get_house_power():
    return house_power + np.random.normal(0, 50)

def get_tesla_power():
    return tesla_power + np.random.normal(0,100)

def get_solar_power():
    return solar_power + np.random.normal(0,100)

@get('/simulator/power')
def simulator_power():
    current_time = datetime.now()
    nearest_row = {}
    
    nearest_row['heater_power'] = get_heater_power()
    nearest_row['twc_power'] = get_tesla_power()
    nearest_row['house_power'] = get_house_power() + nearest_row['twc_power'] + nearest_row['heater_power']
    
    nearest_row['solar_power'] = get_solar_power()
    
    nearest_row['grid_power'] = nearest_row['solar_power'] - nearest_row['house_power']
    
    nearest_row['heater_mode'] = heater_mode
    nearest_row['twc_mode'] = 'eco' # FIXME

    
    
    
    # nearest_index['heater_power'] = heater_power(nearest_index['heater_power'])
    
    # nearest_row = nearest_row + np.random.normal(0, 0.1, len(nearest_row))
    
    return json.dumps({"status": "ok", "data":nearest_row})

@get('/simulator/heater/setmode')
def simulator_heater_setmode():
    global heater_mode
    query = request.query.mode
    if query in available_modes:
        heater_mode = query
        return json.dumps({"status": "ok", "data": heater_mode})
    return json.dumps({"status": "error: unknown mode"})


@get('/simulator/setpower')
def simulator_set_power():
    global heater_power, house_power, tesla_power, solar_power
    heater_p = request.query.heater
    tesla_p = request.query.tesla
    house_p = request.query.house
    solar_p = request.query.solar
    
    try:
        heater_p = int(heater_p)
        tesla_p = int(tesla_p)
        house_p = int(house_p)
        solar_p = int(solar_p)
        print(heater_p,tesla_p,house_p,solar_p)
        
        heater_power = heater_p
        tesla_power = tesla_p
        house_power = house_p
        solar_power = solar_p
        
        
        return json.dumps({"status": "ok", "data": "Power set"})
    except ValueError:
        return json.dumps({"status": "error: invalid power"})
    
        
        
print(''' ▄▄▄▄▄▄▄ ▄▄▄▄▄▄   ▄▄▄ ▄▄▄▄▄▄     ▄▄▄▄▄▄▄ ▄▄▄ ▄▄   ▄▄ ▄▄   ▄▄ ▄▄▄     ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄   
█       █   ▄  █ █   █      █   █       █   █  █▄█  █  █ █  █   █   █       █       █       █   ▄  █  
█   ▄▄▄▄█  █ █ █ █   █  ▄    █  █  ▄▄▄▄▄█   █       █  █ █  █   █   █   ▄   █▄     ▄█   ▄   █  █ █ █  
█  █  ▄▄█   █▄▄█▄█   █ █ █   █  █ █▄▄▄▄▄█   █       █  █▄█  █   █   █  █▄█  █ █   █ █  █ █  █   █▄▄█▄ 
█  █ █  █    ▄▄  █   █ █▄█   █  █▄▄▄▄▄  █   █       █       █   █▄▄▄█       █ █   █ █  █▄█  █    ▄▄  █
█  █▄▄█ █   █  █ █   █       █   ▄▄▄▄▄█ █   █ ██▄██ █       █       █   ▄   █ █   █ █       █   █  █ █
█▄▄▄▄▄▄▄█▄▄▄█  █▄█▄▄▄█▄▄▄▄▄▄█   █▄▄▄▄▄▄▄█▄▄▄█▄█   █▄█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█▄▄█ █▄▄█ █▄▄▄█ █▄▄▄▄▄▄▄█▄▄▄█  █▄█''')

available_modes = ['Normal','Overdrive','Off','Eco']
heater_mode = available_modes[0]

DAY_DATA = date(2022, 6, 10)
now = datetime.now()
dataToStream = db.select_power_day(DAY_DATA) # Will be used to stream data to simulate

solar_power = 10000
heater_power = 6000
tesla_power = 8000
house_power = 500

# FIXME: Will stop working after midnight
dataToStream['time'] = dataToStream['time'].apply(lambda x: datetime.fromisoformat(x).replace(year=now.year,month=now.month,day=now.day))

dataToStream = dataToStream.set_index('time').drop('id',axis=1)
    