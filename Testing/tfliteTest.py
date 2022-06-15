import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
from DeepLearning.DataEngine import Preprocessing
from Tools.SolarLib import ghiToPower

import tensorflow as tf
from Tools.VisualCrossingApi import get_weather_next_day, exampleResponse
import numpy as np


def forecast_power_output(df):
    df["Ghi"] = np.zeros(len(df))
    df["Ghi_NextDay"] = np.zeros(len(df))
    
    
    x,_ = Preprocessing(df)
    
    x = tf.cast(x, tf.float32)
    
    TFLITE_FILE_PATH = './models/VisualCrossing_LSTM_model.h5.tflite'
    # Load the TFLite model in TFLite Interpreter
    interpreter = tf.lite.Interpreter(model_path=TFLITE_FILE_PATH)
    input_data = x
    
    interpreter.allocate_tensors()
    interpreter.set_tensor(interpreter.get_input_details()[0]['index'], input_data)
    
    interpreter.invoke()
    
    output_data = interpreter.get_tensor(interpreter.get_output_details()[0]['index'])

    return [int(ghiToPower(x[0])) for x in output_data]





weatherTomorrow = get_weather_next_day()
power = forecast_power_output(weatherTomorrow)
print(power)