from requests import get
from secret import API_KEY_VC
import pandas as pd
import json
from datetime import datetime


def getForcast():
    r = get(
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/gampelen/tomorrow?include=fcst%2Cobs%2Chistfcst%2Cstats%2Chours&key={API_KEY_VC}&contentType=json")

    if r.status_code == 200:
        return jsonToDF(r.json())
    else:
        return None


def jsonToDF(j):
    hours = j[0]["days"][0]["hours"]

    # Could be done with a single dict and a list comprehension but it's more readable this way
    #'temp', 'feelslike', 'humidity', 'precip', 'windspeed', 'winddir','sealevelpressure', 'cloudcover', 'conditions', 'dayOfTheYear'
    data = {
        "datetime": [datetime.fromtimestamp(x["datetimeEpoch"]).isoformat() for x in hours],
        "temp": [x["temp"] for x in hours],
        "feelslike": [x["feelslike"] for x in hours],
        "humidity":  [x["humidity"] for x in hours],
        "precip": [x["precip"] for x in hours],
        "windspeed": [x["windspeed"] for x in hours],
        "winddir":  [x["winddir"] for x in hours],
        "sealevelpressure": [x["pressure"] for x in hours],
        "cloudcover":  [x["cloudcover"] for x in hours],
        # "conditions": [x["conditions"] for x in hours],
    }

    df = pd.DataFrame(data)
    return df


def exampleResponse(fileName):
    data = []
    with open(fileName) as f:
        data.append(json.load(f))

    return jsonToDF(data)


if __name__ == "__main__":
    fileName = "exampleRequest.json"
    data = []
    with open(fileName) as f:
        data.append(json.load(f))

    df = jsonToDF(data)
    print(df)
    # print(data)
