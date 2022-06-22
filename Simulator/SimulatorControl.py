from sklearn.datasets import make_regression
import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
import streamlit as st
from Tools.ApiRequest import make_request


heater_power = st.slider('Heater power', 0, 10000, 50)
twc_power = st.slider('telsa power', 0, 14000, 50)
house_power = st.slider('House power', 0, 3000, 50)

print(f'http://localhost:8081/simulator/setpower?heater={heater_power}&tesla={twc_power}&house={house_power}')
make_request(f'http://localhost:8081/simulator/setpower?heater={heater_power}&tesla={twc_power}&house={house_power}')
