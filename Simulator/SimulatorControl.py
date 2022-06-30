from sklearn.datasets import make_regression
import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
import streamlit as st
from Tools.ApiRequest import make_request


solar_power = st.slider('Solar power', 0, 20000, 50)
heater_power = st.slider('Heater power', 0, 14000, 50)
twc_power = st.slider('telsa power', 0, 16000, 50)
house_power = st.slider('House power', 0, 3000, 50)

heater_mode = st.selectbox('Heater mode', ['normal', 'overdrive'])

make_request(f'http://localhost:8080/simulator/setpower?heater={heater_power}&tesla={twc_power}&house={house_power}&solar={solar_power}')

make_request(f'http://localhost:8080/simulator/heater/setmode?mode={heater_mode}')