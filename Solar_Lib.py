
from datetime import datetime,timedelta
import pytz
import pandas as pd

def tetha(date,lat=47,lon=7.02):
    from pysolar.solar import get_altitude
    
    return get_altitude(lat, lon, date)

if __name__=="__main__":
    d = datetime.fromisoformat("2022-08-22 00:00:00")
    d = pytz.utc.localize(d)
    
    heights = []
    hours = []
    
    while d.day != 23:
        height = tetha(d)
        if height >= 0:
            heights.append(height)
            hours.append(d.hour)
        d += timedelta(hours=1)
        
    from matplotlib import pyplot as plt
    
    # plt.plot(hours,heights)
    # plt.show()
    
    df = pd.read_csv("data/Crunched/solcastOneDay.csv")
    df = df.drop(df.columns.difference(["Dni","Ghi","Dhi"]), axis=1)
    
    df["tetha"] = [tetha (datetime.fromisoformat(x)) for x in df["datetime"]]