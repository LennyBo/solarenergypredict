import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
import time
import schedule
from datetime import datetime,timedelta
from DatabaseModule import DatabaseModule
from Tools.VisualCrossingApi import get_weather_next_day
from Testing.ApiForecast import forecast_power_output
import requests
from datetime import date
from Tools.Telegram import easy_message
from Tools.ApiRequest import make_request

every = 1 # minutes

def get_next_job_time(time, interval):
    next_job_time = time.replace(second=0, microsecond=0)
    next_job_time = next_job_time + timedelta(minutes=next_job_time.minute//interval * interval + interval - next_job_time.minute)
    
    return next_job_time

def log_power():
    print(f'{datetime.now()} job')
    try:
        data = make_request('http://localhost:8080/house/power')['data']
        
        db.insert_power_data(data)

        df = db.select_power_day(date.today())

        # print(df)
        
        # print(db.select_energy_day())
        # print(db.select_energy_day(date.today() + timedelta(days=1)))
    except requests.exceptions.ConnectionError:
        print('No connection to API')
    finally:
        nextJobTime = get_next_job_time(datetime.now(), every)
        schedule.every((nextJobTime - datetime.now()).total_seconds()).seconds.do(log_power)
    
    return schedule.CancelJob

def control_components():
    print("Control components")
    try:
        # Get current state of components
        data = make_request('http://localhost:8080/house/power')['data']
        heater_power = data['heater_power']
        twc_power = data['twc_power']
        heater_mode = data['heater_mode']
        twc_mode = data['twc_mode']
        
        
        # Get current state of grid
        grid_power = data['grid_power']
        
        # Decide what components to turn up/down
        if grid_power < -1000: # We are buying power from the grid
            # Turn components down
            if heater_mode == 'overdrive': #and heater_power < 2000: # If the heater is currently running, it is not good practice to force stop it
                # Turn heater down
                print('Turning heater down')
                make_request('http://localhost:8080/house/heater?mode=normal')
            elif twc_power > 1000: # Tesla is charging
                print('Stopping tesla charge') # Does not work so no request just for testing
        elif grid_power + heater_power > 6000: # We are selling power to the grid
            if heater_mode == 'normal':
                # Turn heater up
                print('Turning heater up')
                make_request('http://localhost:8080/house/heater?mode=overdrive')
            elif twc_power < 1000: # Tesla is not charging
                print('Starting tesla charge')
            
    except requests.exceptions.ConnectionError:
        print('No connection to API') # Since it is every minute we can just wait for the next job
    
    
    
    
    
    
    

def update_power_prediction_nextday():
    # TODO Handle exceptions
    #Insert prediction for tomorrow
    prediction = forecast_power_output(get_weather_next_day())[0]
    db.insert_energy_day(
                           {'solar_energy':0,'solar_predicted':prediction,'grid_energy':0,'twc_energy':0,
                            'twc_green_precentage':0,'heater_energy':0,
                            'heater_green_precentage':0,'house_energy':0,
                            'house_green_precentage':0},
                           date.today() + timedelta(days=1))


db = DatabaseModule('data/SolarDatabase.db',False)

update_power_prediction_nextday()
log_power()
schedule.every().day.at("20:00").do(update_power_prediction_nextday)
schedule.every().minute.do(control_components)


while True:
    try:
        schedule.run_pending()
    except Exception as e:
        easy_message(f'Script encoutered an error\n{e}') # Send error through telegram
    finally:
        time.sleep(1) # Every second, see if there is a job to run
