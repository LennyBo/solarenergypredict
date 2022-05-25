import matplotlib.pyplot as plt
import numpy as np
from DataEngine import loadDFsToCrunch,Preprocessing

from keras import layers
from keras.models import Sequential
from keras.layers import Dense
from sklearn.metrics import mean_absolute_error, mean_squared_error

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Removes console spam

def mean(array):
    return sum(array)/len(array)


def getBaselines(x, y):
    """Returns mae and mse of the 2 arrrays"""
    return (round(mean_absolute_error(x, y), roundDecimal), round(mean_squared_error(x, y), roundDecimal))


def printBaseLine(y, roundDecimal=2):
    """prints baselines of the y axis

    Args:
        y (arraylike): y axis to evaluate
        roundDecimal (int, optional): amount of decimals to round to. Defaults to 2.
    """
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
    """Plots metric history of each epoch

    Args:
        history (array): History of the training
        metrics (array): each metrics name (used for the legend)
    """
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
    EPOCHS = 55
    BATCH_SIZE = 256
    TEST_SIZE = 0.16 # Precent
    VAL_SIZE = 360 # Days
    SAVE_MODEL = True
    SAVE_FILE = "./models/VisualCrossing_LSTM_model.h5"
    
    
    print("Loading dataset...")
    df = loadDFsToCrunch()
    print(f"Loaded {len(df)} rows\tStartDate: {df.index[0]}\tEndDate: {df.index[-1]}\n")
    
    print("Preprocessing...")
    x,y = Preprocessing(df)
    print(f"Done preprocessing.\tX: {len(x)} shape:{x.shape}\tY: {len(y)}\n")
    
    print(f"Splitting into train val and test with test size {TEST_SIZE * 100}%...")
    length = len(y)
    X_train, X_test, y_train, y_test = (
        x[0:int(length*(1-TEST_SIZE))],
        x[int(length*(1-TEST_SIZE)):],
        y[0:int(length*(1-TEST_SIZE))],
        y[int(length*(1-TEST_SIZE)):],
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
    
    print("Compiling model...\n")
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
    
    print(f"Training with epochs={EPOCHS} batch_size={BATCH_SIZE}...\n")

    trainHistory = model.fit(
        X_train, y_train, 
        epochs=EPOCHS, batch_size=BATCH_SIZE, 
        verbose=1,validation_data=(X_val, y_val)
    )

    score = model.evaluate(X_test, y_test, verbose=0)

    roundDecimal = 2
    print("\n\nTest results:")
    print('Mean absolute error:', round(score[1], roundDecimal))
    print('Mean squared error :', round(score[0], roundDecimal))

    printBaseLine(y_test, roundDecimal)

    plot_metrics(trainHistory, metrics=["mean_absolute_error"])
    plt.show()

    if SAVE_MODEL:
        model.save(SAVE_FILE)
        print(f"Model saved to {SAVE_FILE}")
