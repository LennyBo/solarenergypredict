
import sys
sys.path.append('.')  # Adds parent directory so we can import other modules
import unittest
from DeepLearning.DataEngine import loadDFsToCrunch, Preprocessing
import numpy as np
from Tools.VisualCrossingApi import get_weather_next_day
from Tools.ForecastPower import forecast_power_output

class UnitTest(unittest.TestCase):

    
    def test_loading(self):
        df = loadDFsToCrunch()
        self.assertGreater(len(df), 0)
        self.assertEqual(len(df.columns), 12)
    
    def test_preprocessing(self):
        df = loadDFsToCrunch()
        x,y = Preprocessing(df)
        
        self.assertEqual(len(x), len(y))
        self.assertEqual(x.shape, (len(x), 24,9))
        self.assertEqual(y.shape, (len(y), 4))
        self.assertFalse(np.any(np.isnan(x)))
        self.assertFalse(np.any(np.isnan(y)))
        
        x, y = Preprocessing(df,24) # Changes to no split on y axis

        self.assertEqual(len(x), len(y))
        self.assertEqual(x.shape, (len(x), 24, 9))
        self.assertEqual(y.shape, (len(y), 1))
        self.assertFalse(np.any(np.isnan(x)))
        self.assertFalse(np.any(np.isnan(y)))
        
    def test_apiCall(self):
        df = get_weather_next_day()
        
        self.assertEqual(len(df), 24)
        self.assertEquals(len(df.columns), 11)
        
    def test_tflite_model(self):
        df = get_weather_next_day()
        forcast = forecast_power_output(df)
        
        self.assertEqual(len(forcast), 1)
        self.assertGreater(sum(forcast[0]), 0)
        
    
        

if __name__ == '__main__':
    unittest.main()
