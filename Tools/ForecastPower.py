import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
from DeepLearning.DataEngine import Preprocessing
from Tools.SolarLib import ghiToPower
import tensorflow.lite as tflite
from Tools.VisualCrossingApi import get_weather_next_day
import numpy as np

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '4' # Removes console spam


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
    
    return [[int(ghiToPower(x)) for x in p] for p in output_data]
    

if __name__ == "__main__":
    predictions = forecast_power_output(get_weather_next_day())
    
    print(predictions)
    print(sum(predictions[0]))