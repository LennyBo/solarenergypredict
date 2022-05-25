# imports the two solar installation at my home
from SolarTools.Solar_Lib import solarSouth, solarNorth, ghiToPower
from tensorflow import keras
from SolarTools.VisualCrossingApi import getForcast, exampleResponse
from datetime import datetime
import numpy as np
from tensorflow.keras.utils import to_categorical

model = keras.models.load_model('models/VisualCrossing_LSTM_model.h5')

# df = exampleResponse("exampleRequest.json")
df = getForcast()

forecastStart = 6  # 6 am
forecastTime = 12  # 12 hours after 6 am
x = []
# df["conditions"] = to_categorical(np.asarray(df["conditions"].factorize()[0]))
# print(df["conditions"])

dateTs = []
for i in range(0+forecastStart, len(df), 24):
    xTemp = df[i:i+forecastTime].drop(["datetime"], axis=1)
    dateTs.append(datetime.fromisoformat(df["datetime"][i]))
    dayOfTheYear = datetime.fromisoformat(
        df["datetime"][i]).timetuple().tm_yday

    xTemp["dayOfTheYear"] = [dayOfTheYear] * forecastTime
    print(xTemp.columns)
    xTemp = np.asarray(xTemp)
    x.append(xTemp)

x = np.asarray(x).astype('float32')
print(x.shape)
res = model.predict(x)


print(dateTs)
for Ghi, dateT in zip(res, dateTs):
    Ghi = Ghi[0]
    solarOutput = ghiToPower(Ghi, dateT)

    print(f"{dateT.date()} : {round(solarOutput / 1000, 2)} kWh")
