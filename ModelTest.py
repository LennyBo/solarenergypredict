import matplotlib.pyplot as plt
from tensorflow import keras
import pandas as pd
from datetime import datetime, date
import numpy as np
from Solar_Lib import ghiToPower
from sklearn.metrics import mean_absolute_error

# Time to execute 42s
forecastStart = 0  # 6 am
forecastTime = 24  # 12 hours after 6 am


df_weather = pd.read_csv("data/Crunched/S_V_Dev9.csv")
df_SolarEdge = pd.read_csv("data/SolarEdge/SolarEdgeCut.csv")

startDateTest = df_SolarEdge["date"][0]
endDateTest = df_SolarEdge["date"][len(df_SolarEdge) - 1]


df_weather = df_weather[df_weather["datetime"] >=
                        startDateTest]
df_weather = df_weather[df_weather["datetime"] <=
                        endDateTest]

df_weather = df_weather.reset_index()
df_weather.drop(["windgust", "index"], axis=1, inplace=True)

df_weather[df_weather.columns.difference(["Ghi", "Ghi_NextDay"])] = df_weather[df_weather.columns.difference(
    ["Ghi", "Ghi_NextDay"])].fillna(0)

df_weather.dropna(inplace=True)
df_weather.drop(["Ghi", "conditions"], axis=1, inplace=True)


dates = []
x = []
y_calced = []

for i in range(0+forecastStart, len(df_weather) - 24, 24):
    xTemp = df_weather[i:i +
                       forecastTime].drop(["datetime", "Ghi_NextDay"], axis=1)
    dates.append(datetime.fromisoformat(
        df_weather["datetime"][i])
    )
    dayOfTheYear = datetime.fromisoformat(
        df_weather["datetime"][i]).timetuple().tm_yday
    xTemp["dayOfTheYear"] = [dayOfTheYear] * forecastTime

    xTemp = np.asarray(xTemp)
    x.append(xTemp)
    y_calced.append(ghiToPower(
        sum(df_weather["Ghi_NextDay"][i:i + forecastTime]), dates[-1]))

x = np.asarray(x).astype('float32')

# model = keras.models.load_model('models/VisualCrossing_LSTM_model.h5')
model = keras.models.load_model('models/400MaeModel.h5')

y_pred = model.predict(x)  # Predicts sum Ghi of each date


y_pred = [ghiToPower(y, d)[0]
          for y, d in zip(y_pred, dates)]  # Converts to power (wh)


df = pd.DataFrame({"date": dates, "y_pred": y_pred})
df.set_index("date", inplace=True)

df_SolarEdge["date"] = [datetime.fromisoformat(
    s) for s in df_SolarEdge["date"]]

print(df_SolarEdge["date"][0] == pd.Timestamp(dates[0].date()))
y_true = []
for e, d1, d2 in zip(df_SolarEdge["energy"], df_SolarEdge["date"], dates):
    if (d1.date() != d2.date()):
        print(f"ERROR: Dates are not continuous {d1} {d2}")
    y_true.append(e)


df["y_true"] = y_true
df["y_calced"] = y_calced


mae = mean_absolute_error(y_true, y_pred)
print(df)
df.plot()

print(f"Mean absolute error: {round(mae / 1000,2)} kwh")
plt.show()
# print(df_SolarEdge[dates[0].date().isoformat()])
