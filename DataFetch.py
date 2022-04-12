import pandas as pd
from datetime import datetime
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import os


import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from keras.models import Sequential
from keras.layers import Dense
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import mean_squared_error

forecastStart = 6 # 6 am
forecastTime = 12 # 12 hours after 6 am

def crunchVisualCrossingSolcast(df_weather,df_solar,outPutFile):
    """
    Takes the GHI of the solcast set and the weather
    of the visualCrossing set and puts it togetgher
    """
    # df_solar = pd.read_csv(solcastFile)
    
    # # Transform from str into datetime
    
    
    # df_weather = pd.read_csv(visualCrossingFile)
    
    #print(datetime.fromisoformat(df_weather["datetime"][0]))
    
    df_solar["datetime"] = [datetime.fromisoformat((x[:-1])) for x in df_solar["PeriodStart"]]
    df_solar = df_solar.set_index("datetime")
    
    df_solar.drop(df_solar.columns.difference(
            ["Ghi"]), axis=1, inplace=True)
    
    df_weather["datetime"] = [datetime.fromisoformat(x) for x in df_weather["datetime"]]
    
    df_weather = df_weather.set_index("datetime")
    
    df_weather.drop(df_weather.columns.difference(
            ["temp","feelslike","humidity","precip","windgust",
             "windspeed","winddir","sealevelpressure","cloudcover","conditions"]
            ), axis=1, inplace=True)
    
    df_weather = df_weather.join(df_solar)
    
    
    df_weather['Ghi_NextDay'] = df_weather['Ghi'].shift(periods=-24)
    cols_to_shift = df_weather.columns.difference(["Ghi","Ghi_NextDay"])
    
    df_weather[cols_to_shift] = df_weather[cols_to_shift].shift(periods=-24)
    
    df_weather.to_csv(outPutFile, mode='w', index=True,header=True)
    
def loadCrunchedSolVC(file):
    
    #df = pd.read_csv(file).fillna(method="backfill").fillna(method="backfill").fillna(method="ffill").fillna(0)
    df = pd.read_csv(file).fillna(0)
    
    
    df["conditions"] = to_categorical(np.asarray(df["conditions"].factorize()[0]))
    x = []
    y = []
    tab_mse = []
    
    for i in range(0+forecastStart,len(df) - 24,24): # I chose +3 since with the longest day, we have the first sun rays at 3am
        dayOfTheYear = datetime.fromisoformat(df["datetime"][i]).timetuple().tm_yday
        mse = mean_squared_error(df["Ghi"][i:i+forecastTime],df["Ghi_NextDay"][i:i+forecastTime])
        tab_mse.append(mse)
        xTemp = df[i:i+forecastTime].drop(["datetime","Ghi_NextDay"],axis=1)
        #print(f"{xTemp.iloc()[0]['datetime']} {xTemp.iloc()[-1]['datetime']}")
        #xTemp = np.append(xTemp,[dayOfTheYear],axis=0)
        x.append(np.asarray(xTemp).flatten() + [dayOfTheYear])
        y.append(np.array(df["Ghi_NextDay"][i:i+forecastTime]))
    mse = np.mean(tab_mse)
    return x,y,mse

def getFiles(inputDir):
    filesArray = []

    for _root, _dirs, files in os.walk(inputDir):
        for file in files:
            filesArray.append(inputDir + file)
    
    return filesArray
    
def loadDFsToCrunch():
    weatherCSVs = getFiles("./data/VisualCrossing/")
    df_weather = pd.read_csv(weatherCSVs[0])
    for f in weatherCSVs[1::]:
        df_weather = pd.concat([df_weather,pd.read_csv(f)],axis=0,ignore_index=True,sort=False)
    
    
    df_solcast = pd.read_csv("./data/solcast/47.014664_7.057895_Solcast_PT60M.csv")
    #crunchVisualCrossingSolcast(df_weather,df_solcast,"./data/Crunched/VisualCrossing_Solcast2.csv")
    return df_weather, df_solcast
    

if __name__ == "__main__":
    
    # df_weather, df_solcast = loadDFsToCrunch()
    # crunchVisualCrossingSolcast(df_weather,df_solcast,"./data/Crunched/S_V_Dev3.csv")
    # exit()
    
    
    
    
    x,y,baselineMSE = loadCrunchedSolVC(
            "data/Crunched/S_V_Dev3.csv"
        )
    
    
    x = np.asarray(x).astype('float32')
    
    # length,sX,yX = x.shape
    # x = x.reshape(length,sX,yX,1)
    y = np.asarray(y)
    
    test_size = 0.33
    length = len(y)
    X_train, X_test, y_train, y_test = (
        x[0:int(length*(1-test_size))],
        x[int(length*(1-test_size)):],
        y[0:int(length*(1-test_size))],
        y[int(length*(1-test_size)):],
    )
    
    scaler = StandardScaler()
    scaler.fit_transform(X_train)
    scaler.transform(X_test)
    
    
    print(f"{len(x)} {len(y_train) + len(y_test)}")
    
    
    model = Sequential()
    #model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(16,16,1)))
    
    model.add(layers.Flatten())
    model.add(Dense(200, activation= "relu"))
    model.add(Dense(100, activation= "relu"))
    model.add(Dense(50, activation= "relu"))
    model.add(Dense(forecastTime, activation= "relu"))
    
    model.compile(loss= "mean_squared_error" , optimizer="adam", metrics=["mean_squared_error"])
    model.fit(X_train, y_train, validation_data=(X_test,y_test),epochs=100)

    
    
    
    
    print(f"Test Baseline : {baselineMSE}")

    
    