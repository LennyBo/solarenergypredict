from datetime import datetime, timedelta

from StateMachine import control_components

from Tools.Console import log
from Tools.ApiRequest import make_request
from Tools.ForecastPower import forecast_power_output
from Tools.VisualCrossingApi import get_weather_next_day

from datetime import date
import requests

from DatabaseModule import database as db
import schedule
import time



every = 1  # minutes


def get_next_job_time(time, interval):
    next_job_time = time.replace(second=0, microsecond=0)
    next_job_time = next_job_time + \
        timedelta(minutes=next_job_time.minute//interval *
                  interval + interval - next_job_time.minute)

    return next_job_time


def log_power():
    log('insert job')
    try:
        data = make_request('http://localhost:8080/house/power')['data']
        # Even if the request wasn't exactly at that time, we move it to it
        data['time'] = datetime.now().replace(
            second=0, microsecond=0).isoformat()
        db.insert_power_data(data)

        # df = db.select_power_day(date.today())

        # log(df)

        # log(db.select_energy_day())
        # log(db.select_energy_day(date.today() + timedelta(days=1)))
    except requests.exceptions.ConnectionError:
        log('No connection to API')
    finally:
        nextJobTime = get_next_job_time(datetime.now(), every)
        schedule.every((nextJobTime - datetime.now()
                        ).total_seconds()).seconds.do(log_power)

    return schedule.CancelJob


def one_shot_night_routine():
    # Insert prediction for tomorrow
    weather = get_weather_next_day()
    if weather is not None:
        prediction = forecast_power_output(weather)[0]
        db.insert_energy_day({'solar_energy': 0, 'solar_predicted': sum(prediction),
                              'solar_night_morning_predicted': prediction[0], 'solar_morning_noon_predicted': prediction[1],
                              'solar_noon_evening_predicted': prediction[2], 'solar_evening_night_predicted': prediction[3],
                              'grid_energy': 0, 'twc_energy': 0,
                              'twc_green_precentage': 0, 'heater_energy': 0,
                              'heater_green_precentage': 0, 'house_energy': 0,
                              'house_green_precentage': 0},
                             date.today() + timedelta(days=1))

        # Decide if we do something
        if prediction[1] < 20000:  # If we have less than 20kW of power in the morning
            log('Set heater overdrive until morning')
            make_request('http://localhost:8080/house/heater?mode=Overdrive')
    else:
        log('No weather data, connection error')


def run_power_logger():
    # one_shot_night_routine() # Only for development
    log_power()
    schedule.every().day.at("23:00").do(one_shot_night_routine)
    schedule.every(15).minutes.do(control_components)

    log('Power logger started')
    while True:
        schedule.run_pending()
        time.sleep(1)  # Every second, see if there is a job to run


if __name__ == '__main__':
    run_power_logger()
