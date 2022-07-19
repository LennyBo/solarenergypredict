import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
from requests import get
import requests
from secret import API_KEY_VC
import pandas as pd
import json
from datetime import datetime


def get_weather_next_day():
    try:
        r = get(
            f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/gampelen/tomorrow?include=fcst%2Cobs%2Chistfcst%2Cstats%2Chours&key={API_KEY_VC}&contentType=json"
        )

        if r.status_code == 200:
            data = json.loads(r.text)
            return jsonToDF(data)
    except requests.exceptions.ConnectionError:
        pass
    return None


def jsonToDF(j):
    hours = j["days"][0]["hours"]

    # Could be done with a single dict and a list comprehension but it's more readable this way
    #'temp', 'feelslike', 'humidity', 'precip', 'windgust', 'windspeed','winddir', 'sealevelpressure', 'cloudcover', 'conditions', 'Ghi','Ghi_NextDay'
    data = {
        "datetime": [datetime.fromtimestamp(x["datetimeEpoch"]).isoformat() for x in hours],
        "temp": [x["temp"] for x in hours],
        "feelslike": [x["feelslike"] for x in hours],
        "humidity":  [x["humidity"] for x in hours],
        "precip": [x["precip"] for x in hours],
        "windgust": [x["windgust"] for x in hours],
        "windspeed": [x["windspeed"] for x in hours],
        "winddir":  [x["winddir"] for x in hours],
        "sealevelpressure": [x["pressure"] for x in hours],
        "cloudcover":  [x["cloudcover"] for x in hours],
        "conditions": [x["conditions"] for x in hours],
    }

    df = pd.DataFrame(data)
    return df




if __name__=="__main__":
    print(get_weather_next_day())