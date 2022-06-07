import sys
from urllib import response

from sklearn.metrics import r2_score
sys.path.append( '.' ) # Adds parent directory so we can import other modules
import time
import schedule
import numpy as np
from datetime import datetime,timedelta
from DatabaseModule import DatabaseModule
from Tools.VisualCrossingApi import getWeatherNextDay
from Testing.ApiForecast import forecast
import requests
from datetime import date

every = 1 # minutes

def get_next_job_time(time, interval):
    next_job_time = time.replace(second=0, microsecond=0)
    next_job_time = next_job_time + timedelta(minutes=next_job_time.minute//interval * interval + interval - next_job_time.minute)
    
    return next_job_time

def update():
    print(f'{datetime.now()} job')
    res = requests.get('http://localhost:8080/house/power')
    if res.status_code == 200:
        data = res.json()
        if data['status'] == 'ok':
            db.insert_data(data['data'])
            db.get_sum()
        else:
            print(f'{datetime.now()} error: {data["status"]}')
    else:
        print("Error: " + str(res.status_code))

    df = db.select_data_day(datetime.now().date())

    print(df)
    print(db.select_daily_energy(datetime.now().date() + timedelta(days=1)))
    nextJobTime = get_next_job_time(datetime.now(), every)
    schedule.every((nextJobTime - datetime.now()).total_seconds()).seconds.do(update)
    
    return schedule.CancelJob

def predict():
    # TODO Handle exceptions
    #Insert prediction for tomorrow
    prediction = forecast(getWeatherNextDay())[0]
    db.insert_daily_energy(
                           {'solar_energy':0,'solar_predicted':prediction,'grid_energy':0,'twc_energy':0,
                            'twc_green_precentage':0,'heater_energy':0,
                            'heater_green_precentage':0,'house_energy':0,
                            'house_green_precentage':0},
                           date.today() + timedelta(days=1))
    



# nextJobTime = get_next_job_time(datetime.now(), every)
# schedule.every((nextJobTime - datetime.now()).total_seconds()).seconds.do(test)

# run(host='localhost', port=8080, debug=True)

db = DatabaseModule('data/SolarDatabase.db',True)

predict()

update()
schedule.every().day.at("20:00").do(update)
while True:
    schedule.run_pending()
    
    

    time.sleep(1)

print(e)
from Tools.Telegram import easyMessage
easyMessage(f"Solar Energy Predict: exception encountered\n{e}")
# from Tools.Telegram import easyMessage
# easyMessage("Solar Energy Predict: exception encountered")
schedule.clear()
    
# threading.Timer(5, update).start()
