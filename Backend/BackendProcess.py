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
from Tools.Console import log
from PowerController import run_power_logger


@get('/house/power/day')
def daily():
    """_summary_: Get the historic power from the database

    Returns:
        json dict: data of the historic power or error message
    """
    try:
        d = request.query.date
        if d == '':
            d = date.today()
        else:
            d = date.fromisoformat(d)
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
    """_summary_: Change the heater mode

    Returns:
        json dict: request status
    """
    state = request.query.mode
    log("Setting heater to " + state)
    if state in ['Overdrive', 'Normal', 'Off', 'Eco']:
        data_parser.set_heater(state)
        return json.dumps({"status": "ok"})
    else:
        return json.dumps({"status": "error expected state: Overdrive, Normal, Off, Eco"})
    
@get('/house/twc')
def house_components():
    """_summary_: Change the tesla wall charger control mode

    Returns:
        json dict: request status
    """
    state = request.query.mode
    log("Setting Tesla to " + state + " control")
    if state in ['Smart Grid', 'Manual']:
        data_parser.set_twc_mode(state)
        return json.dumps({"status": "ok"})
    else:
        return json.dumps({"status": "error expected state: 'Smart Grid', 'Manual'"})
    
@get('/house/energy')
def house_energy():
    """_summary_: Get the historic energy from the database"""
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


@get('/house/power')
def house_power():
    """_summary_: Get the current state of all components

    Returns:
        json dict: request status and data
    """
    return json.dumps({"status": "ok", "data": data_parser.get_power()}).encode('utf-8')
    

@get('/ping')
def power():
    return json.dumps({"status": "pong"}).encode('utf-8')

if __name__ == '__main__':
    print('''
  ____   __    ___  __ _  ____  __ _  ____     __   ____  __  
 (  _ \ / _\  / __)(  / )(  __)(  ( \(    \   / _\ (  _ \(  ) 
  ) _ (/    \( (__  )  (  ) _) /    / ) D (  /    \ ) __/ )(  
 (____/\_/\_/ \___)(__\_)(____)\_)__)(____/  \_/\_/(__)  (__) 

   __    __  __  ____  _   _  _____  ____      __    ____  _  _  _  _  _  _    ____  _____  ____  ___  __    ____ 
  /__\  (  )(  )(_  _)( )_( )(  _  )(  _ \()  (  )  ( ___)( \( )( \( )( \/ )  (  _ \(  _  )( ___)/ __)(  )  (_  _)
 /(__)\  )(__)(   )(   ) _ (  )(_)(  )   /     )(__  )__)  )  (  )  (  \  /    ) _ < )(_)(  )__)( (_-. )(__  _)(_ 
(__)(__)(______) (__) (_) (_)(_____)(_)\_)()  (____)(____)(_)\_)(_)\_) (__)   (____/(_____)(____)\___/(____)(____)
 _   _  ____       __    ____   ___ 
( )_( )( ___)___  /__\  (  _ \ / __)
 ) _ (  )__)(___)/(__)\  )   /( (__ 
(_) (_)(____)   (__)(__)(_)\_) \___)
All rights reserved



''')
    power_data = None

    if platform != 'linux':
        import Simulator.GridSimulator # Will add the routes for the simulator
        data_parser = house_I.Simulated_House()
        # data_parser = house_I.Real_House()
    else:
        data_parser = house_I.Real_House() # if it is running on the pi we always want to do the real calls

    # PowerController runs on a separate process
    thread_controller = Process(target=run_power_logger)
    thread_controller.daemon = True
    thread_controller.start()
    
    run(host='localhost', port=8080, debug=False,server='cheroot')