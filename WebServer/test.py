import streamlit as st
import time
import numpy as np
from PIL import Image
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
        self.solarProd = 0
        self.gridProd = 0
        self.solar = self.column.markdown("")
        self.grid = self.column.markdown("")
    
    def update(self):
        self.api_call()
        
        self.solar.markdown(f'#### Solar: {round(self.solarProd)} kw')
        self.grid.markdown(f'#### Grid: {round(self.gridProd)} kw')
        
    def api_call(self):
        # TODO: Modbus call
        self.solarProd = self.solarProd + np.random.uniform(-100,200)
        self.gridProd = self.gridProd + np.random.uniform(-100,100)
        
class HeaterWidget (UpdateingWidget):
    
    def __init__(self, column):
        super().__init__(column,'Webserver/images/heater_logo.png')
        
    
    def init(self):
        self.i = 0
        self.mode = self.column.markdown("#### Mode: Overdrive")
        self.powerToday = self.column.markdown("#### Power today: 16 kwh")
        self.powerDistributionLabel = self.column.markdown("#### Power distribution: 10%")
        self.powerDistributionProg = self.column.progress(self.i)
        
    def update(self):
        self.i += 1
        
        # self.mode = self.column.markdown("#### Mode: Overdrive")
        # self.powerToday = self.column.markdown("#### Power today: 16 kwh")
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
        
def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


local_css("WebServer/style.css")

st.sidebar.header("Tesla Wall Charger")

colsPerRow = 3
widgetCount = 3
grid = []

wc = WidgetController(colsPerRow,widgetCount)

wc.add_widget(SolarWidget)
wc.add_widget(HeaterWidget)
wc.add_widget(TeslaWallChargerWidget)

while True:
    wc.update_all()
    time.sleep(1)

