import sys


sys.path.append( '.' ) # Adds parent directory so we can import other modules
import json
from Tools.Shelly import heater_power, tesla_power
from bottle import run, post, request, response,get
from datetime import date,datetime
import numpy as np
from Backend.DatabaseModule import DatabaseModule
from Tools.SolarEdgeModbus import CallModbus

def get_rnd_value():
    return np.random.randint(0, 100)

#TODO change to /house/power
@get('/solar/day')
def daily():
    
    try:
        d = request.query.date
        if d == '':
            d = date.today()
        else:
            d = date.fromisoformat(d)
        
        # data = json.loads(request.body.read().decode('utf-8'))
        
        # d = date.fromisoformat(data['date'])
        
        df = db.select_data_day(d)
        return json.dumps({"status": "ok", "data": df.to_dict()})
    except KeyError:
        return json.dumps({"status": "error expected key: date"})
    except ValueError:
        return json.dumps({"status": "error date format"})
    except Exception as e:
        print(e)
        return json.dumps({"status": "unknown error"})


@get('/house/energy')
def house_energy():
    try:
        d = request.query.date
        if d == '':
            d = date.today()
        else:
            d = date.fromisoformat(d)
        
        energy = db.select_daily_energy(d).to_dict()
        if len(energy['date']) == 0: # Means it is in the future
            return json.dumps({"status": "error: No data for that day"})
        
        dict_ = {
            'solar_predicted': energy['solar_predicted'][0],
            'solar_energy': energy['solar_energy'][0],
            'grid_energy': energy['grid_energy'][0],
            'twc_energy': energy['twc_energy'][0],
            'heater_energy': energy['heater_energy'][0],
            'house_energy': energy['house_energy'][0],
        }
        
        return json.dumps({"status": "ok", "data": dict_})
    except KeyError:
        return json.dumps({"status": "error expected key: date"})
    except ValueError:
        return json.dumps({"status": "error date format"})
    # except Exception as e:
    #     print(e)
    #     return json.dumps({"status": "unknown error"})

@get('/house/power')
def house_power():
    d = datetime.now().replace(second=0, microsecond=0)
    # solar_edge = CallModbus()
    # tesla = tesla_power()
    # heater = heater_power()
    di = {
        'time':d.isoformat(),
        # 'solar_power': solar_edge['solar'], 
        # 'grid_power': solar_edge['grid'], 
        # 'house_power': solar_edge['house'], 
        # 'twc_power': tesla, 
        # 'heater_power': heater,
        'solar_power': get_rnd_value(), 
        'grid_power': get_rnd_value(), 
        'house_power': get_rnd_value(), 
        'twc_power': get_rnd_value(), 
        'heater_power': get_rnd_value(),
        'heater_mode': 'Overdrive',
        'twc_mode': 'Eco'
        }
    return json.dumps({"status": "ok", "data": di}).encode('utf-8')
    
@get('/ping')
def power():
    return ["pong"]


db = DatabaseModule('data/SolarDatabase.db')
run(host='localhost', port=8080, debug=False,server='cheroot')