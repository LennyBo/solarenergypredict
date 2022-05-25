from datetime import datetime
import numpy as np
import pandas as pd
import os


def JoinSolcastVC(df_weather, df_solar):
    """
    Takes the Ghi of the solcast set and the weather
    of the visualCrossing set and puts it togetgher
    """
    # df_solar = pd.read_csv(solcastFile)

    # # Transform from str into datetime

    # df_weather = pd.read_csv(visualCrossingFile)

    # print(datetime.fromisoformat(df_weather["datetime"][0]))

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


def Preprocessing(df):
    forecastLength = 24
    df = df.reset_index()
    # Process Nan's
    df.drop(["windgust"], axis=1, inplace=True)

    df[df.columns.difference(["Ghi", "Ghi_NextDay"])] = df[df.columns.difference(["Ghi", "Ghi_NextDay"])].fillna(0)
    df.dropna(inplace=True)

    df.drop(["Ghi", "conditions"], axis=1, inplace=True)

    # df["conditions"] = to_categorical(
    #     np.asarray(df["conditions"].factorize()[0]))

    x = []
    y = []

    for i in range(0, len(df) - 24, 24):
        xTemp = df[i:i+forecastLength].drop(["datetime", "Ghi_NextDay"], axis=1)
        # Adding day of the year to the set
        dayOfTheYear = df["datetime"][i].timetuple().tm_yday
        xTemp["dayOfTheYear"] = [dayOfTheYear] * forecastLength

        xTemp = np.asarray(xTemp)
        x.append(xTemp)
        y.append([sum(np.array(df["Ghi_NextDay"][i:i+forecastLength]))])

    return np.asarray(x), np.asarray(y)


def getFiles(inputDir):
    filesArray = []

    for _root, _dirs, files in os.walk(inputDir):
        for file in files:
            filesArray.append(inputDir + file)

    return filesArray


def loadDFsToCrunch(dataDir="./data/"):
    weatherCSVs = getFiles(dataDir + "VisualCrossing/")
    df_weather = pd.read_csv(weatherCSVs[0])
    
    for f in weatherCSVs[1::]:
        df_weather = pd.concat([df_weather, pd.read_csv(
            f)], axis=0, ignore_index=True, sort=False)

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
    
    print(f"Done splitting.\tTrain: {len(X_train)}\tVal: {len(X_val)}\tTest: {len(X_test)}\n")
