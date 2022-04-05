import pandas as pd
from datetime import datetime
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from keras.models import Sequential
from keras.layers import Dense


def crunchVisualCrossingSolcast(visualCrossingFile,solcastFile,outPutFile):
    """
    Takes the GHI of the solcast set and the weather
    of the visualCrossing set and puts it togetgher
    """
    df_solar = pd.read_csv(solcastFile)
    
    # Transform from str into datetime
    
    
    df_weather = pd.read_csv(visualCrossingFile)
    
    # print(datetime.fromisoformat(df_weather["datetime"][0]))
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
    
    df_weather.to_csv(outPutFile, mode='w', index=True,header=True)
    
def loadCrunchedSolVC(file):
    
    df = pd.read_csv(file).fillna(method="backfill").fillna(method="backfill").fillna(method="ffill").fillna(0)
    
    dictConditions = {"Clear":0,"Rain":1,"Snow":3}
    
    df["conditions"] = [dictConditions[x] for x in df["conditions"]]
    x = []
    y = []
    for i in range(0+3,len(df) - 24,24): # I chose +3 since with the longest day, we have the first sun rays at 3am
        dayOfTheYear = datetime.fromisoformat(df["datetime"][i]).timetuple().tm_yday
        xTemp = np.array(df[i:i+16].drop(["datetime","Ghi_NextDay"],axis=1)).flatten()
        xTemp = np.append(xTemp,[dayOfTheYear],axis=0)
        x.append(xTemp)
        y.append(np.array(df["Ghi_NextDay"][i:i+16]))
    
    scaler = StandardScaler()
    x = scaler.fit_transform(x)
    
    return x,y
        
    
    
if __name__ == "__main__":
    x,y = loadCrunchedSolVC(
            "data/Crunched/S_V_Dev.csv"
        )
    x = np.asarray(x)
    y = np.asarray(y)
    
    X_train, X_test, y_train, y_test = train_test_split(
                        x, y, test_size=0.33, random_state=42)
    
    model = Sequential()
    model.add(Dense(500, activation= "relu"))
    model.add(Dense(100, activation= "relu"))
    model.add(Dense(50, activation= "relu"))
    model.add(Dense(16))
    
    model.compile(loss= "mean_squared_error" , optimizer="adam", metrics=["mean_squared_error"])
    model.fit(X_train, y_train, epochs=20)  

    
    