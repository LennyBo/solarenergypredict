import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta, date
import numpy as np
from sklearn.preprocessing import StandardScaler
import os


from keras import layers
from keras.models import Sequential
from keras.layers import Dense
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import mean_absolute_error, mean_squared_error

forecastStart = 0  # 6 am
forecastTime = 24  # 12 hours after 6 am


def crunchVisualCrossingSolcast(df_weather, df_solar, outPutFile):
    """
    Takes the Ghi of the solcast set and the weather
    of the visualCrossing set and puts it togetgher
    """
    # df_solar = pd.read_csv(solcastFile)

    # # Transform from str into datetime

    # df_weather = pd.read_csv(visualCrossingFile)

    # print(datetime.fromisoformat(df_weather["datetime"][0]))

    df_solar["datetime"] = [datetime.fromisoformat(
        (x[:-1])) for x in df_solar["PeriodStart"]]
    df_solar = df_solar.set_index("datetime")

    df_solar.drop(df_solar.columns.difference(
        ["Ghi"]), axis=1, inplace=True)

    df_weather["datetime"] = [datetime.fromisoformat(
        x) for x in df_weather["datetime"]]

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

    print(df_weather.isna().sum())

    df_weather.to_csv(outPutFile, mode='w', index=True, header=True)


def loadCrunchedSolVC(file):

    #df = pd.read_csv(file).fillna(method="backfill").fillna(method="backfill").fillna(method="ffill").fillna(0)

    df = pd.read_csv(file)

    df.drop(["windgust"], axis=1, inplace=True)

    df[df.columns.difference(["Ghi", "Ghi_NextDay"])] = df[df.columns.difference(
        ["Ghi", "Ghi_NextDay"])].fillna(0)
    df.dropna(inplace=True)

    df.drop(["Ghi", "conditions"], axis=1, inplace=True)

    testingDate = datetime.fromisoformat(df["datetime"][0])
    datesToDelete = []
    for col in df["datetime"][0:-1]:
        dateTime = datetime.fromisoformat(col)
        if dateTime != testingDate:
            # print(f"ERROR: Dates are not continuous {dateTime}")
            datesToDelete.append(dateTime.date())
            testingDate = dateTime
        testingDate += timedelta(hours=1)

    # df["conditions"] = to_categorical(
    #     np.asarray(df["conditions"].factorize()[0]))

    x = []
    y = []

    # I chose +3 since with the longest day, we have the first sun rays at 3am
    for i in range(0+forecastStart, len(df) - 24, 24):

        # print(df[i:i+forecastTime])

        # print(datetime.fromisoformat(df["datetime"][i]).timetuple().tm_yday)

        xTemp = df[i:i+forecastTime].drop(["datetime", "Ghi_NextDay"], axis=1)
        dayOfTheYear = datetime.fromisoformat(
            df["datetime"][i]).timetuple().tm_yday
        xTemp["dayOfTheYear"] = [dayOfTheYear] * forecastTime

        #print(f"{xTemp.iloc()[0]['datetime']} {xTemp.iloc()[-1]['datetime']}")
        xTemp = np.asarray(xTemp)

        #xTemp = np.append(xTemp,[dayOfTheYear],axis=0)

        x.append(xTemp)
        y.append([sum(np.array(df["Ghi_NextDay"][i:i+forecastTime]))])

    return x, y


def mean(array):
    return sum(array)/len(array)


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
        df_weather = pd.concat([df_weather, pd.read_csv(
            f)], axis=0, ignore_index=True, sort=False)

    df_solcast = pd.read_csv(
        "./data/solcast/47.014664_7.057895_Solcast_PT60M.csv")
    # crunchVisualCrossingSolcast(df_weather,df_solcast,"./data/Crunched/VisualCrossing_Solcast2.csv")
    return df_weather, df_solcast


def getBaselines(x, y):
    return (round(mean_absolute_error(x, y), roundDecimal), round(mean_squared_error(x, y), roundDecimal))


def printBaseLine(y, roundDecimal=2):
    meanX = [mean(y)] * len(y)
    medianX = [np.median(y)] * len(y)
    shiftedX = y[:-1:]
    shiftedY = y[1::]

    print(f"\nMean y_test : {round(meanX[0][0],roundDecimal)}")
    print(f"Median y_test : {round(medianX[0],roundDecimal)}")

    mae, mse = getBaselines(meanX, y)
    print(f"Mean baseline: mae : {mae}, mse : {mse}")
    mae, mse = getBaselines(medianX, y)
    print(f"Median baseline: mae : {mae}, mse : {mse}")
    mae, mse = getBaselines(shiftedX, shiftedY)
    print(f"Shifted baseline: mae : {mae}, mse : {mse}")


def plot_metrics(history, metrics):
    for n, metric in enumerate(metrics):
        name = metric.replace("_", " ").capitalize()
        plt.subplot(len(metrics), 1, n+1)
        plt.plot(history.epoch,
                 history.history[metric], color="C1", label='Train')
        plt.plot(history.epoch, history.history['val_'+metric],
                 color="C0", linestyle="--", label='Val')
        plt.xlabel('Epoch')
        plt.ylabel(name)

        plt.legend()


if __name__ == "__main__":
    file = "./data/Crunched/S_V_Dev9.csv"

    df_weather, df_solcast = loadDFsToCrunch()
    crunchVisualCrossingSolcast(df_weather, df_solcast, file)

    x, y = loadCrunchedSolVC(file)

    x = np.asarray(x).astype('float32')

    # length,sX,yX = x.shape
    # x = x.reshape(length,sX,yX,1)
    y = np.asarray(y)

    test_size = 0.16
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

    # scaler = StandardScaler()
    # X_train = scaler.fit_transform(X_train)
    # X_test = scaler.transform(X_test)

    # scaler = StandardScaler()
    # y_train = scaler.fit_transform(y_train)
    # y_test = scaler.transform(y_test)

    print(
        f"Datapoints: {len(x)}, y_train len: {len(y_train) },y_val len: {len(y_val) }, y_test len: {len(y_test)}")

    model = Sequential()
    model.add(layers.BatchNormalization(input_shape=(x[0].shape)))
    model.add(layers.Conv1D(filters=64, kernel_size=3, activation='relu'))
    model.add(layers.MaxPooling1D(pool_size=2))
    # model.add(layers.Conv1D(filters=64, kernel_size=3, activation='relu'))
    model.add(layers.LSTM(units=64, return_sequences=True))
    # model.add(layers.BatchNormalization())
    model.add(layers.Flatten())
    model.add(Dense(200, activation="relu"))
    model.add(Dense(100, activation="relu"))
    model.add(Dense(50, activation="relu"))
    model.add(layers.Dropout(0.2))
    model.add(Dense(1))

    model.compile(loss="mean_squared_error", optimizer="adam",
                  metrics=["mean_absolute_error"])

    # tf.keras.utils.plot_model(model, to_file="NN_Diagramm.png", show_shapes=True)

    rollingWindow = 1000
    batchsize = 64
    # for i in range(0, len(X_train) - rollingWindow, 10):
    #     model.fit(X_train[i:i+rollingWindow], y_train[i:i+rollingWindow], epochs=1, batch_size=batchsize, verbose=1,
    #               validation_data=(X_val, y_val)
    #               )

    trainHistory = model.fit(X_train, y_train, epochs=55, batch_size=batchsize, verbose=1,
                             validation_data=(X_val, y_val)
                             )

    score = model.evaluate(X_test, y_test, verbose=0)

    roundDecimal = 2
    print("\n\nTest results:")
    print('Mean absolute error:', round(score[1], roundDecimal))
    print('Mean squared error :', round(score[0], roundDecimal))

    printBaseLine(y_test, roundDecimal)

    plot_metrics(trainHistory, metrics=["mean_absolute_error"])
    plt.show()

    model.save("./models/VisualCrossing_LSTM_model.h5")
