import streamlit as st
import time
import numpy as np
from PIL import Image
import requests
from datetime import datetime
st.set_page_config(layout="wide") # Needs to be the first st command



class WidgetController:
    def __init__(self,cols,widgetCount) -> None:
        self.cols = cols
        self.widgetCount = widgetCount
        self.grid = []
        self.x = 0
        self.y = 0
        self.widgets = []
        
        for i in range(widgetCount//colsPerRow):
            grid.append(st.columns(colsPerRow))

        if widgetCount % colsPerRow != 0:
            grid.append(st.columns(widgetCount % colsPerRow))
    
    def add_widget(self, widget) -> None:
        self.widgets.append(widget(grid[self.y][self.x]))
        
        self.x = (self.x + 1) % self.cols
        if self.x == 0:
            self.y = self.y + 1
            
    def update_all(self):
        for w in self.widgets:
            w.update()

class UpdateingWidget:
    def __init__(self, column,imagePath):
        try:
            image = Image.open(imagePath)
            column.image(image,width=60)
        except FileNotFoundError:
            print(f"Image {imagePath} not found, leaving blank")

        self.column = column
        self.init()
        self.update()
        
    def init(self):
        pass
    
    def update(self):
        pass
    
class SolarWidget (UpdateingWidget):
    def __init__(self, column):
        super().__init__(column,'WebServer/images/solar_logo.png')
        
    def init(self):
        self.solar = self.column.markdown("")
        self.grid = self.column.markdown("")
    
    def update(self):        
        self.solar.metric(label='Solar: ',value=f'{currentData["solar_power"]} kw')# ,delta=-1.2)
        self.grid.metric(label='Grid: ',value=f'{currentData["grid_power"]} kw')
        
class HeaterWidget (UpdateingWidget):
    
    def __init__(self, column):
        super().__init__(column,'Webserver/images/heater_logo.png')
        
    
    def init(self):
        self.i = 0
        self.mode = self.column.markdown("#### Mode: Overdrive")
        self.powerToday = self.column.markdown("#### Power : 16 kw")
        self.powerDistributionLabel = self.column.markdown("#### Power distribution: 10%")
        self.powerDistributionProg = self.column.progress(self.i)
        
    def update(self):
        self.i += 1
        
        # self.mode = self.column.markdown("#### Mode: Overdrive")
        self.powerToday.markdown(f'#### Power : {currentData["heater_power"]} kw')
        # self.column.markdown("#### Power distribution: 10%")
        self.powerDistributionLabel.markdown(f"#### Power distribution: {self.i}%")
        self.powerDistributionProg.progress(self.i % 100)
        return super().update()
          
class TeslaWallChargerWidget (UpdateingWidget):
    
    def __init__(self, column):
        super().__init__(column,'Webserver/images/tesla_logo.png')
        
    def init(self):
        self.mode = self.column.markdown("#### Mode: ECO")
        self.charging = self.column.markdown("#### Chargin: Yes")
        
        self.column.markdown("#### Power Today: 10%")
        self.powerDistribution = self.column.progress(10)
        
def apiUpdate():
    res = requests.get('http://localhost:8080/house/power')
    if res.status_code == 200:
        jsonRes = res.json()
        if jsonRes['status'] == 'ok':
            return jsonRes['data']
        else:
            print(f'{datetime.now()} error: {jsonRes["status"]}')
    else:
        print("Error: " + str(res.status_code))        

def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

currentData = apiUpdate()

local_css("WebServer/style.css")

# st.sidebar.header("Tesla Wall Charger")

colsPerRow = 3
widgetCount = 3
grid = []

wc = WidgetController(colsPerRow,widgetCount)

wc.add_widget(SolarWidget)
wc.add_widget(HeaterWidget)
wc.add_widget(TeslaWallChargerWidget)

import pandas as pd

res = requests.get('http://localhost:8080/solar/day')
if res.status_code == 200:
    data = res.json()
    if data['status'] == 'ok':
        df = pd.DataFrame(data['data'])
    else:
        print(f'{datetime.now()} error: {data["status"]}')
else:
    print("Error: " + str(res.status_code))

df['time'] = df['time'].apply(lambda x: datetime.fromisoformat(x))
df.set_index('time', inplace=True)

sliced = df['2022-06-02 12:50':'2022-06-02 13:30']
print(sliced)

df['import'] = df['grid_power'].apply(lambda x: abs(x) if x < 0 else 0)
df['export'] = df['grid_power'].apply(lambda x: x if x > 0 else 0)
df['selfused'] = df['solar_power'] - df['export']


df = df.drop(df.columns.difference(['import','export','selfused']), axis=1)

import altair as alt
data = df.T.reset_index()
data = pd.melt(data, id_vars=["index"]).rename(columns={"index": "type", "value": "power"})
chart = (
    alt.Chart(data)
    .mark_area(opacity=0.6)
    .encode(
        x="time:T",
        y=alt.Y("power:Q", stack=True),
        color="type:N",
        tooltip=['time',"power","type"]
    )
)
st.altair_chart(chart, use_container_width=True)

while True:
    currentData = apiUpdate()
    wc.update_all()
    time.sleep(1)

