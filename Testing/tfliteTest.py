import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
from sys import platform
from DeepLearning.DataEngine import Preprocessing
from Tools.SolarLib import ghiToPower

if platform == "linux" or platform == "linux2": # Since we can't use tensorflow on the pi, we use tflite_runtime there
    import tflite_runtime.interpreter as tflite
else:
    import tensorflow.lite as tflite
    # import tflite_runtime.interpreter as tflite

from Tools.VisualCrossingApi import get_weather_next_day, exampleResponse
import numpy as np

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Removes console spam


def forecast_power_output(df):
    df["Ghi"] = np.zeros(len(df))
    df["Ghi_NextDay"] = np.zeros(len(df))
    
    
    x,_ = Preprocessing(df)
    
    x = np.float32(x)
    
    TFLITE_FILE_PATH = './models/VisualCrossing_LSTM_model.h5.tflite'
    # Load the TFLite model in TFLite Interpreter
    interpreter = tflite.Interpreter(model_path=TFLITE_FILE_PATH)
    input_data = x
    
    interpreter.allocate_tensors()
    interpreter.set_tensor(interpreter.get_input_details()[0]['index'], input_data)
    
    interpreter.invoke()
    
    output_data = interpreter.get_tensor(interpreter.get_output_details()[0]['index'])

    return [int(ghiToPower(x[0])) for x in output_data]



if __name__ == "__main__":
    weatherTomorrow = get_weather_next_day()
    power = forecast_power_output(weatherTomorrow)
    print(power)