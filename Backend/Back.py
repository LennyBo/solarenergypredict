import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
import time
import schedule
import numpy as np
from datetime import datetime,timedelta
from DatabaseModule import DatabaseModule


every = 1 # minutes

def get_rnd_value():
    return np.random.randint(0, 100)

def get_next_job_time(time, interval):
    next_job_time = time.replace(second=0, microsecond=0)
    next_job_time = next_job_time + timedelta(minutes=next_job_time.minute//interval * interval + interval - next_job_time.minute)
    
    return next_job_time

def update():
    print(f'{datetime.now()} job')
    db.insert_data({'SOLAR_POWER': get_rnd_value(), 'GRID_POWER': get_rnd_value(), 'HOUSE_POWER': get_rnd_value(), 'TWC_POWER': get_rnd_value(), 'HEAT_POWER': get_rnd_value(), 'HEATER_MODE': 'Overdrive'})
    df = db.select_data_day(datetime.now().date())

    # print(df)
    nextJobTime = get_next_job_time(datetime.now(), every)
    schedule.every((nextJobTime - datetime.now()).total_seconds()).seconds.do(update)
    
    return schedule.CancelJob



db = DatabaseModule('data/SolarDatabase.db')

update()

# nextJobTime = get_next_job_time(datetime.now(), every)
# schedule.every((nextJobTime - datetime.now()).total_seconds()).seconds.do(test)
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
finally:
    from Tools.Telegram import easyMessage
    easyMessage("Solar Energy Predict: exception encountered")
    schedule.clear()
# threading.Timer(5, update).start()
