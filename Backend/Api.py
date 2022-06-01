import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
import json
from bottle import run, post, request, response,get
from datetime import date,datetime
import numpy as np
from Backend.DatabaseModule import DatabaseModule

def get_rnd_value():
    return np.random.randint(0, 100)

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
        return json.dumps({"status": "ok", "data": df.to_dict()}).encode('utf-8')
    except KeyError:
        return json.dumps({"status": "error expected key: date"})
    except ValueError:
        return json.dumps({"status": "error date format"})
    except Exception as e:
        print(e)
        return json.dumps({"status": "unknown error"})

db = DatabaseModule('data/SolarDatabase.db')

@get('/house/power')
def power():
    d = datetime.now().replace(second=0, microsecond=0)
    di = {
        'time':d.isoformat(),
        'solar_power': get_rnd_value(), 
        'grid_power': get_rnd_value(), 
        'house_power': get_rnd_value(), 
        'twc_power': get_rnd_value(), 
        'heater_power': get_rnd_value(),
        'heater_mode': 'Overdrive'
        }
    return json.dumps({"status": "ok", "data": di}).encode('utf-8')
    
@get('/ping')
def power():
    return ["pong"]

run(host='localhost', port=8080, debug=False,server='cheroot')