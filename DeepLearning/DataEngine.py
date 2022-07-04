from datetime import datetime
import numpy as np
import pandas as pd
import os


def JoinSolcastVC(df_weather, df_solar):
    """
    Takes the Ghi of the solcast set and the weather
    of the visualCrossing set and puts it togetgher
    """
    df_solar["datetime"] = [datetime.fromisoformat((x[:-1])) for x in df_solar["PeriodStart"]]
    df_solar = df_solar.set_index("datetime")

    df_solar.drop(df_solar.columns.difference(["Ghi"]), axis=1, inplace=True)

    df_weather["datetime"] = [datetime.fromisoformat(x) for x in df_weather["datetime"]]

    df_weather = df_weather.set_index("datetime")

    df_weather.drop(df_weather.columns.difference(
        ["temp", "feelslike", "humidity", "precip", "windgust",
         "windspeed", "winddir", "sealevelpressure", "cloudcover", "conditions"]
    ), axis=1, inplace=True)

    df_weather = df_weather.join(df_solar)

    df_weather['Ghi_NextDay'] = df_weather['Ghi'].shift(periods=-24)
    cols_to_shift = df_weather.columns.difference(["Ghi", "Ghi_NextDay"])

    df_weather[cols_to_shift] = df_weather[cols_to_shift].shift(periods=-24)

    df_weather.drop(df_weather.tail(24).index, inplace=True)

    # print(df_weather.isna().sum())

    return df_weather

def Preprocessing(df,hour_split=6): # hour_split = 0-6 7-12 13-18 19-24
    # 24 hours each day (we could slice just the day part but it does not improve the model and makes everything more complicated)
    forecastLength = 24
    # If datetime is the index, we need to move it back into the set
    if "datetime" not in df.columns:
        df = df.reset_index()
        
    # Process Nan's
    df.drop(["windgust","Ghi", "conditions"], axis=1, inplace=True) # These clumns are not needed to improve predictions
    
    # Fillna 0 on all the columns except Ghi and Ghi_NextDay as these two have nan's only because the set ends sooner
    df[df.columns.difference(["Ghi", "Ghi_NextDay"])] = df[df.columns.difference(["Ghi", "Ghi_NextDay"])].fillna(0)
    
    # This will remove all the rows that have nan's in the Ghi and Ghi_NextDay columns $
    df.dropna(inplace=True)
    
    if(df["datetime"].dtype != "datetime64[ns]"):
        df["datetime"] = pd.to_datetime(df["datetime"])
    
    x = []
    y = []
    for i in range(0, len(df), 24): # For each 24 hours
        xTemp = df[i:i+forecastLength].drop(["datetime", "Ghi_NextDay"], axis=1) # Slice the day
        
        # Adding day of the year to the set
        dayOfTheYear = df["datetime"][i].timetuple().tm_yday
        xTemp["dayOfTheYear"] = [dayOfTheYear] * len(xTemp)

        xTemp = np.asarray(xTemp)#.reshape(len(xTemp), len(xTemp.columns),1)
        # xTemp = np.concatenate((xTemp, xTemp,xTemp), axis=2) # Resnet needs 3 channels
        
        x.append(xTemp)
        
        y.append([sum(np.array(df["Ghi_NextDay"][x:x+hour_split])) for x in range(i, i+forecastLength,hour_split)]) # Add the sum ghi of the next day to y

    return np.asarray(x), np.asarray(y)

def getFiles(inputDir):
    filesArray = []

    for _root, _dirs, files in os.walk(inputDir):
        for file in files:
            filesArray.append(_root + file)

    return filesArray

def loadDFsToCrunch(dataDir="./data/"):
    weatherCSVs = getFiles(dataDir + "VisualCrossing/")
    df_weather = pd.read_csv(weatherCSVs[0])
    
    for f in weatherCSVs[1::]:
        df_weather = pd.concat([df_weather, pd.read_csv(f)], axis=0, ignore_index=True, sort=False)

    df_solcast = pd.read_csv(dataDir + "solcast/47.014664_7.057895_Solcast_PT60M.csv")

    return JoinSolcastVC(df_weather, df_solcast)


if __name__ == "__main__":
    print("Loading dataset...")
    df = loadDFsToCrunch()
    print(f"Loaded {len(df)} rows\tStartDate: {df.index[0]}\tEndDate: {df.index[-1]}\n")
    print("Preprocessing...")
    x,y = Preprocessing(df)
    print(f"Done preprocessing.\tX: {len(x)}\tY: {len(y)}\n")
    
    test_size = 0.16
    print(f"Splitting into train val and test with test size {test_size * 100}%...")
    
    length = len(y)
    X_train, X_test, y_train, y_test = (
        x[0:int(length*(1-test_size))],
        x[int(length*(1-test_size)):],
        y[0:int(length*(1-test_size))],
        y[int(length*(1-test_size)):],
    )
    val_length = 360
    length = len(y_train)

    X_train, X_val, y_train, y_val = (
        X_train[0:length - val_length],
        X_train[length - val_length:],
        y_train[0:length - val_length],
        y_train[length - val_length:],
    )
    
    print(y.shape)
    
    print(f"Done splitting.\tTrain: {len(X_train)}\tVal: {len(X_val)}\tTest: {len(X_test)}\n")
