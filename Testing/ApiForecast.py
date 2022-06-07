import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
from DeepLearning.DataEngine import Preprocessing
from Tools.SolarLib import ghiToPower
from tensorflow import keras
from Tools.VisualCrossingApi import getWeatherNextDay, exampleResponse
from datetime import datetime
import numpy as np

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Removes tensorflow console spam

MODEL_TO_LOAD = 'VisualCrossing_LSTM_model.h5'


def forecast(df):
    df["Ghi"] = np.zeros(len(df))
    df["Ghi_NextDay"] = np.zeros(len(df))
    
    model = keras.models.load_model('models/' + MODEL_TO_LOAD)
    
    x,_ = Preprocessing(df)

    res = model.predict(x)

    return [int(x[0]) for x in res]
    

if __name__ == "__main__":
    predictions = forecast(getWeatherNextDay())
    
    print(predictions)