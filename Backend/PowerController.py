import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
import time
import schedule
from datetime import datetime,timedelta
from DatabaseModule import DatabaseModule
from Tools.VisualCrossingApi import get_weather_next_day
from Tools.ForecastPower import forecast_power_output
import requests
from datetime import date
from Tools.Telegram import easy_message
from Tools.ApiRequest import make_request
from StateMachine import control_components

every = 1 # minutes

house_lat = 47.0142651
house_lon = 7.0556118



    

def get_next_job_time(time, interval):
    next_job_time = time.replace(second=0, microsecond=0)
    next_job_time = next_job_time + timedelta(minutes=next_job_time.minute//interval * interval + interval - next_job_time.minute)
    
    return next_job_time

def log_power():
    print(f'{datetime.now()} job')
    try:
        data = make_request('http://localhost:8080/house/power')['data']
        data['time'] = datetime.now().replace(second=0, microsecond=0).isoformat() # Even if the request wasn't exactly at that time, we move it to it
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

    
    
    
def update_power_prediction_nextday():
    # TODO Handle exceptions
    #Insert prediction for tomorrow
    prediction = forecast_power_output(get_weather_next_day())[0]
    db.insert_energy_day({'solar_energy':0,'solar_predicted':prediction,'grid_energy':0,'twc_energy':0,
                            'twc_green_precentage':0,'heater_energy':0,
                            'heater_green_precentage':0,'house_energy':0,
                            'house_green_precentage':0},
                           date.today() + timedelta(days=1))
    

def run_power_logger():
    global db
    db = DatabaseModule('data/SolarDatabase.db',False)

    update_power_prediction_nextday()
    log_power()
    schedule.every().day.at("20:00").do(update_power_prediction_nextday)
    schedule.every(5).minutes.do(control_components)

    print('Power logger started')
    while True:
        schedule.run_pending()
        time.sleep(1) # Every second, see if there is a job to run


if __name__=='__main__':
    run_power_logger()