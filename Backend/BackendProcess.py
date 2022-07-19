import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules

from platform import platform
import json
from sys import platform
from bottle import run, request,get
from datetime import date
from Backend.DatabaseModule import database as db
import HouseInterface as house_I
from multiprocessing import Process

from PowerController import run_power_logger


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
    
@get('/house/heater')
def house_components():
    state = request.query.mode
    print(state)
    if state in ['Overdrive', 'Normal', 'Off', 'Eco']:
        data_parser.set_heater(state)
        return json.dumps({"status": "ok"})
    else:
        return json.dumps({"status": "error expected state: Overdrive, Normal, Off, Eco"})
    
@get('/house/twc')
def house_components():
    state = request.query.mode
    print(state)
    if state in ['Smart Grid', 'Manual']:
        data_parser.set_twc_mode(state)
        return json.dumps({"status": "ok"})
    else:
        return json.dumps({"status": "error expected state: 'Smart Grid', 'Manual'"})
    
@get('/house/energy')
def house_energy():
    try:
        d = request.query.date
        if d == '':
            d = date.today()
        else:
            d = date.fromisoformat(d)
        
        energy = db.select_energy_day(d).to_dict()
        if len(energy['date']) == 0: # Means it is in the future or not logged
            return json.dumps({"status": "error: No data for that day"})
        
        dict_ = {
            'solar_predicted': energy['solar_predicted'][0],
            'solar_night_morning_predicted':energy['solar_night_morning_predicted'][0], 
            'solar_morning_noon_predicted':energy['solar_morning_noon_predicted'][0], 
            'solar_noon_evening_predicted':energy['solar_noon_evening_predicted'][0], 
            'solar_evening_night_predicted':energy['solar_evening_night_predicted'][0], 
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
    return json.dumps({"status": "pong"}).encode('utf-8')

if __name__ == '__main__':
    power_data = None
    print(''' ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄   ▄ ▄▄▄▄▄▄▄ ▄▄    ▄ ▄▄▄▄▄▄  ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄ 
█  ▄    █       █       █   █ █ █       █  █  █ █      ██       █       █   █
█ █▄█   █   ▄   █       █   █▄█ █    ▄▄▄█   █▄█ █  ▄    █   ▄   █    ▄  █   █
█       █  █▄█  █     ▄▄█      ▄█   █▄▄▄█       █ █ █   █  █▄█  █   █▄█ █   █
█  ▄   ██       █    █  █     █▄█    ▄▄▄█  ▄    █ █▄█   █       █    ▄▄▄█   █
█ █▄█   █   ▄   █    █▄▄█    ▄  █   █▄▄▄█ █ █   █       █   ▄   █   █   █   █
█▄▄▄▄▄▄▄█▄▄█ █▄▄█▄▄▄▄▄▄▄█▄▄▄█ █▄█▄▄▄▄▄▄▄█▄█  █▄▄█▄▄▄▄▄▄██▄▄█ █▄▄█▄▄▄█   █▄▄▄█''')
    if platform != 'linux':
        import Simulator.GridSimulator # Will add the routes for the simulator
        data_parser = house_I.Simulated_House()
        # data_parser = house_I.Real_House()
    else:
        data_parser = house_I.Real_House() # if it is running on the pi we always want to do the real calls

    thread_controller = Process(target=run_power_logger)
    thread_controller.daemon = True
    thread_controller.start()
    
    run(host='localhost', port=8080, debug=False,server='cheroot')

