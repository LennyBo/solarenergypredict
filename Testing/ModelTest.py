import sys
sys.path.append( '.' )
from DeepLearning.DataEngine import Preprocessing,loadDFsToCrunch

import matplotlib.pyplot as plt
from tensorflow import keras
import pandas as pd
from datetime import datetime
from Tools.SolarLib import ghiToPower
from sklearn.metrics import mean_absolute_error


import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Removes console spam

print("loading data...")
df_weather = loadDFsToCrunch("./data/")
df_SolarEdge = pd.read_csv("data/SolarEdge/SolarEdgeCut.csv") # Cointains y_true


# Because the solaresge data is shorter than the weather data, all excess is cut off 
print("cutting data...")
startDateTest = (datetime.fromisoformat(df_SolarEdge["date"][0])).date()
endDateTest = (datetime.fromisoformat(df_SolarEdge["date"][len(df_SolarEdge) - 1])).date()

df_weather = df_weather[df_weather.index >= startDateTest.isoformat()]
df_weather = df_weather[df_weather.index <= endDateTest.isoformat()]

df_weather = df_weather.fillna(0) # Because other wise, the preprocessing will cut off a few rows of data we want to keep

dates = df_weather.index[:len(df_weather["Ghi_NextDay"].dropna()):24].tolist() # This will create a list of dates the model will predict

print("preprocessing data...")
x, y = Preprocessing(df_weather)


print("predicting...")
model = keras.models.load_model('./models/VisualCrossing_LSTM_model.h5')
# model = keras.models.load_model('models/400MaeModel.h5')
y_pred = model.predict(x)  # Predicts sum Ghi of each date

y_pred = [sum(x) for x in y_pred]
y_calced = [sum(x) for x in y]

print("calculating wh...")
# Transforming the ghi to wh
y_pred = [ghiToPower(y) for y, d in zip(y_pred, dates)]  # Converts to power (wh)
y_calced = [ghiToPower(y) for y, d in zip(y_calced, dates)]  # Converts to power (wh)

print("plotting...")
df_SolarEdge["date"] = [datetime.fromisoformat(s) for s in df_SolarEdge["date"]]

if df_SolarEdge["date"][0] != pd.Timestamp(dates[0].date()):
    print("Error: The start dates are not equal")
    exit(-1)
y_true = []

for e, d1, d2 in zip(df_SolarEdge["energy"], df_SolarEdge["date"], dates):
    if (d1.date() != d2.date()):
        print(f"ERROR: Dates are not continuous {d1} {d2}")
        exit(-1)
    y_true.append(e)

yf = y.flatten()
# Create a df to plot all the values
df = pd.DataFrame({"date": dates, "y_pred": y_pred,"y_true": y_true, "y_calced": y_calced})
df.set_index("date", inplace=True)


mae = mean_absolute_error(y_true, y_pred)
df.plot()

print(f"Mean absolute error: {round(mae / 1000,2)} kwh")

plt.show()
# print(df_SolarEdge[dates[0].date().isoformat()])
