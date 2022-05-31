import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
from DeepLearning.DataEngine import Preprocessing
from SolarTools.SolarLib import ghiToPower
from tensorflow import keras
from SolarTools.VisualCrossingApi import getForcast, exampleResponse
from datetime import datetime
import numpy as np

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Removes console spam

MODEL_TO_LOAD = 'VisualCrossing_LSTM_model.h5'

print(f"Loading model {MODEL_TO_LOAD}...")
model = keras.models.load_model('models/' + MODEL_TO_LOAD)

print("Getting forecast...")
# df = exampleResponse("exampleRequest.json")
df = getForcast()

dateStrs = df["datetime"][0::24].tolist()
# print(dateStrs)

print("Predicting power output...")

df["Ghi"] = np.zeros(len(df))
df["Ghi_NextDay"] = np.zeros(len(df))

x,_ = Preprocessing(df)

res = model.predict(x)


for Ghi, dateStr in zip(res, dateStrs):
    dateT = datetime.fromisoformat(dateStr)
    Ghi = Ghi[0]
    solarOutput = ghiToPower(Ghi)

    print(f"Forecast for the : {dateT.date()} -> {round(solarOutput / 1000, 2)} kWh")
