import sys

from matplotlib.style import available
sys.path.append( '.' ) # Adds parent directory so we can import other modules
from bottle import run, post, request, response,get
from datetime import datetime, date
from Backend.DatabaseModule import database as db
import json
import numpy as np

print(''' ▄▄▄▄▄▄▄ ▄▄▄▄▄▄   ▄▄▄ ▄▄▄▄▄▄     ▄▄▄▄▄▄▄ ▄▄▄ ▄▄   ▄▄ ▄▄   ▄▄ ▄▄▄     ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄   
█       █   ▄  █ █   █      █   █       █   █  █▄█  █  █ █  █   █   █       █       █       █   ▄  █  
█   ▄▄▄▄█  █ █ █ █   █  ▄    █  █  ▄▄▄▄▄█   █       █  █ █  █   █   █   ▄   █▄     ▄█   ▄   █  █ █ █  
█  █  ▄▄█   █▄▄█▄█   █ █ █   █  █ █▄▄▄▄▄█   █       █  █▄█  █   █   █  █▄█  █ █   █ █  █ █  █   █▄▄█▄ 
█  █ █  █    ▄▄  █   █ █▄█   █  █▄▄▄▄▄  █   █       █       █   █▄▄▄█       █ █   █ █  █▄█  █    ▄▄  █
█  █▄▄█ █   █  █ █   █       █   ▄▄▄▄▄█ █   █ ██▄██ █       █       █   ▄   █ █   █ █       █   █  █ █
█▄▄▄▄▄▄▄█▄▄▄█  █▄█▄▄▄█▄▄▄▄▄▄█   █▄▄▄▄▄▄▄█▄▄▄█▄█   █▄█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█▄▄█ █▄▄█ █▄▄▄█ █▄▄▄▄▄▄▄█▄▄▄█  █▄█''')

available_modes = ['normal','overdrive','off']
heater_mode = available_modes[0]

DAY_DATA = date(2022, 6, 10)
now = datetime.now()
dataToStream = db.select_power_day(DAY_DATA) # Will be used to stream data to simulate

 # FIXME: Will stop working after midnight
dataToStream['time'] = dataToStream['time'].apply(lambda x: datetime.fromisoformat(x).replace(year=now.year,month=now.month,day=now.day))

dataToStream = dataToStream.set_index('time').drop('id',axis=1)

def heater_power(historic_heater):
    return historic_heater

@get('/simulator/power')
def simulator_power():
    current_time = datetime.now()
    nearest_index = dataToStream.index.get_indexer([current_time], method='nearest')
    nearest_row = dataToStream.iloc[nearest_index[0]].to_dict()
    
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


run(host='localhost', port=8081, debug=False,server='cheroot')
    
