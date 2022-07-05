import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
import streamlit as st
import time
import numpy as np
from PIL import Image
import requests
from datetime import datetime,date, timedelta
import pandas as pd
from Tools.ApiRequest import make_request

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
        self.txtSolar = self.column.empty()
        self.txtGrid = self.column.empty()
    
    def update(self):
        self.txtSolar.metric(label='Solar: ',value=f'{currentData["solar_power"]} kw',
                             delta=round(currentData["solar_power"] - pastData["solar_power"],1))
        self.txtGrid.metric(label='Grid: ',value=f'{currentData["grid_power"]} kw',
                            delta=round(currentData["grid_power"] - pastData["grid_power"],1))
        
class HeaterWidget (UpdateingWidget):
    
    def __init__(self, column):
        super().__init__(column,'WebServer/images/heater_logo.png')
        
    
    def init(self):
        self.i = 0
        self.txtMode = self.column.empty()
        self.txtCurrentPower = self.column.empty()
        # self.txtPowerDistribution = self.column.empty()
        # self.prgPowerDistributionProg = self.column.progress(self.i)
        
    def update(self):
        self.i += 1
        
        self.txtMode.metric(label="Mode",value=f'{currentData["heater_mode"]}')
        self.txtCurrentPower.metric(label="Power",value=f'{currentData["heater_power"]} kw',
                                    delta=round(currentData["heater_power"] - pastData["heater_power"],1))
        # self.column.markdown("#### Power distribution: 10%")
        # self.txtPowerDistribution.markdown(f"#### Power distribution: {self.i}%")
        # self.prgPowerDistributionProg.progress(self.i % 100)
        return super().update()
          
class TeslaWallChargerWidget (UpdateingWidget):
    
    def __init__(self, column):
        super().__init__(column,'WebServer/images/tesla_logo.png')
        
    def init(self):
        self.radioMode = self.column.radio(label="Mode",options=["Smart Grid","Manual"],index=['Smart Grid','Manual'].index(currentData["twc_mode"]),on_change=self.mode_change)
        self.txtCurrentPower = self.column.empty()
    
    def mode_change(self):
        make_request('http://localhost:8080/house/tesla')
            
    def update(self):
        self.txtCurrentPower.metric(label="Power",value=f'{currentData["twc_power"]} kw',
                                    delta=round(currentData["twc_power"] - pastData["twc_power"],1))
        return super().update()
        
def apiUpdate():
    d = make_request('http://localhost:8080/house/power')['data']
    d = {k:to_kilo(v) for k,v in d.items()}
    return d      

def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

def get_daily_data(d):
    data = make_request('http://localhost:8080/house/power/day?date=' + d.strftime('%Y-%m-%d'))['data']
    return pd.DataFrame(data)
    
        
def get_day_summary(d):
    data = make_request('http://localhost:8080/house/energy?date=' + d.strftime('%Y-%m-%d'))
    if 'data' in data.keys():
        return data['data']
    return None

def get_date():
    getQ = st.experimental_get_query_params()
    if 'date' in getQ:
        dStr = getQ['date'][0]
        try:
            return datetime.strptime(dStr, '%Y-%m-%d')
        except ValueError:
            st.error(f'Invalid date format: {dStr}')
    return date.today()
    
def to_kilo(v):
    if type(v) != int and type(v) != float:
        return v
    return round(v / 1000,1)


date_ = get_date() # Get the date to fetch data for
currentData = apiUpdate() # Initialize with the current values
pastData = currentData

local_css("WebServer/style.css")


# Is for the widget grid
colsPerRow = 3
widgetCount = 3
grid = []

wc = WidgetController(colsPerRow,widgetCount) # Creates columns for the grid

# Adding widgets into the columns
wc.add_widget(SolarWidget)
wc.add_widget(HeaterWidget)
wc.add_widget(TeslaWallChargerWidget)





# Get minutetly data for the selected date
df = get_daily_data(date_)
daySummary = get_day_summary(date_)
# Creates a index for each minute so if there is missing data it will still show 24 hours
dfDates = pd.DataFrame({'time':pd.date_range(start=date_, end=date_+timedelta(days=1),freq='min')})
dfDates = dfDates.set_index('time')

df['time'] = df['time'].apply(lambda x: datetime.fromisoformat(x))
df.set_index('time', inplace=True)

# Will merge the data with the index for 24 hours
df = dfDates.join(df, how='left').fillna(0)

df.index = df.index.tz_localize('Europe/Berlin') # Otherwise altair fucks it up for no reason

# Do some processing for the graph
df["house_power"] = df["house_power"] - df["heater_power"] - df["twc_power"]
df["twc_power"] = df["twc_power"]
df["heater_power"] = df["heater_power"]
df['import'] = df['grid_power'].apply(lambda x: abs(x) if x < 0 else 0)
df['export'] = df['grid_power'].apply(lambda x: x if x > 0 else 0)

# Only keep to info we want to show
df = df.drop(df.columns.difference(['heater_power','twc_power',"house_power","export"]), axis=1)

# Altair sorts the columns alphabetically, and there seems to be no way to hard code which color goes for what
# so we need to sort them manually
df = df.rename(columns={"heater_power":"2_Heater","twc_power":"1_Tesla","house_power":"3_House","export":"0_Export"})


# Altair sorts the columns alphabetically, and there seems to be no way to hard code which color goes for what
# so we need to sort them manually
df = df.rename(columns={"heater_green":"2_House_green","heater_red":"1_House_red","export":"0_Export"})

colors = ['#00ff00','#ff1803','#e4852b','#0000ff']

import altair as alt
data = df.T.reset_index()
data = pd.melt(data, id_vars=["index"]).rename(columns={"index": "type", "value": "power"})



st.title(f"Power summary of the {date_.strftime('%d-%m-%Y')}")
if daySummary is not None:
    cols = st.columns(5)
    
    daySummary = {k:to_kilo(v) for k,v in daySummary.items()}

    cols[0].metric(label="Solar",value=f'{daySummary["solar_energy"]} kwh')
    cols[0].metric(label="Predicted",value=f'{daySummary["solar_predicted"] } kwh')
    cols[1].metric(label="Grid",value=f'{daySummary["grid_energy"]} kwh')
    cols[2].metric(label="Heater",value=f'{daySummary["heater_energy"]} kwh') 
    cols[3].metric(label="Tesla",value=f'{daySummary["twc_energy"]} kwh') 
    cols[4].metric(label="House",value=f'{daySummary["house_energy"]} kwh') 

colPrev,_,colNext = st.columns(3)


colPrev.write(f"<a href='?date={(date_ - timedelta(days=1)).strftime('%Y-%m-%d')}' target='_self'><-</a>", unsafe_allow_html=True)
colNext.write(f"<a href='?date={(date_ + timedelta(days=1)).strftime('%Y-%m-%d')}' target='_self'>-></a>", unsafe_allow_html=True)

chart = (
    alt.Chart(data)
    .mark_area(opacity=0.6)
    .encode(
        x="time:T",
        y=alt.Y("power:Q", stack=True),
        color=alt.Color("type:N", scale=alt.Scale(range=colors)),
        tooltip=['time',"power","type"]
    )
)
st.altair_chart(chart, use_container_width=True)

while True:
    pastData = currentData
    currentData = apiUpdate()
    wc.update_all()
    time.sleep(5)

