import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
from DeepLearning.DataEngine import Preprocessing
from Tools.SolarLib import ghiToPower
from tensorflow import keras
from Tools.VisualCrossingApi import get_weather_next_day, exampleResponse
from datetime import datetime
import numpy as np
import tensorflow_addons as tfa

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Removes tensorflow console spam

MODEL_TO_LOAD = 'VisualCrossing_Transformer_401.67'
# MODEL_TO_LOAD = 'VisualCrossing_LSTM_model.h5'


def forecaset_power_output(df):
    df["Ghi"] = np.zeros(len(df))
    df["Ghi_NextDay"] = np.zeros(len(df))
    
    model = keras.models.load_model('models/' + MODEL_TO_LOAD)
    
    x,_ = Preprocessing(df)

    res = model.predict(x)

    return [int(ghiToPower(x[0])) for x in res]
    

if __name__ == "__main__":
    predictions = forecaset_power_output(get_weather_next_day())
    
    print(predictions)