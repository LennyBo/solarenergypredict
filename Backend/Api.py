import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules

import json
from Tools.Shelly import heater_power, tesla_power
from bottle import run, post, request, response,get
from datetime import date,datetime
import numpy as np
from Backend.DatabaseModule import database as db
import Dataparser as dp


#TODO change to /house/power
@get('/house/power/day')
def daily():
    
    try:
        d = request.query.date
        if d == '':
            d = date.today()
        else:
            d = date.fromisoformat(d)
        
        # data = json.loads(request.body.read().decode('utf-8'))
        
        # d = date.fromisoformat(data['date'])
        
        df = db.select_power_day(d)
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
        
        energy = db.select_energy_day(d).to_dict()
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
    
    return json.dumps({"status": "ok", "data": data_parser.get_power()}).encode('utf-8')
    
@get('/ping')
def power():
    return ["pong"]

data_parser = dp.Simulator_Dataparser()

run(host='localhost', port=8080, debug=False,server='cheroot')