
from datetime import datetime, timedelta
import pytz
import pandas as pd
from math import radians
from cmath import sin
from pysolar.solar import get_altitude
import pandas as pd


def DateToZenith(date, lat=47, lon=7.02):
    try:
        timezone = pytz.timezone("Europe/Zurich")  # FIXME with lat lon
        date = timezone.localize(date)
    except:
        pass

    # for somereason, if the datetime is in a df, get_altitude() raises an exeption so we need to cast it if it is a datetime
    if(type(date) == pd._libs.tslibs.timestamps.Timestamp):
        date = date.to_pydatetime()
    return 90 - get_altitude(lat, lon, date)


def Gti(ebh, zenith, tilt):
    zenith = radians(zenith)
    tilt = radians(tilt)
    return ebh * sin(zenith + tilt).real


def meanEbhToHourly(ebh, date):
    zenithsDate = [(90-DateToZenith(date + timedelta(hours=x)), date + timedelta(hours=x)) for x in range(24) if DateToZenith(
        date + timedelta(hours=x)) <= 90]  # we only want zeniths that are less than 90 degrees and then invert them
    zeniths = [x[0] for x in zenithsDate]
    dateTs = [x[1] for x in zenithsDate]

    factors = [x * (1/sum(zeniths)) for x in zeniths]
    ebhHourly = [f * ebh for f in factors]
    df = pd.DataFrame({"datetime": dateTs, "Ebh": ebhHourly})

    return df


def ebhToPower(ebh, date):

    df = meanEbhToHourly(ebh, date)

    powerSouth = [solarSouth.ebhToPower(x, y)
                  for x, y in zip(df["Ebh"], df["datetime"])]
    powerNorth = [solarNorth.ebhToPower(
        x, y.to_pydatetime()) for x, y in zip(df["Ebh"], df["datetime"])]

    powerTotal = [x+y for x, y in zip(powerSouth, powerNorth)]

    return sum(powerTotal)


class SolarPanels:

    def __init__(self, surface, tilt, efficiency=0.19, lat=47, lon=7.02) -> None:
        self.surface = surface
        self.tilt = tilt
        self.efficiency = efficiency
        self.lat = lat
        self.lon = lon

    def power(self, gti):
        return self.surface * gti * self.efficiency

    def ebhToPower(self, ebh, dateT):
        zenith = DateToZenith(dateT, self.lat, self.lon)
        return self.power(Gti(ebh, zenith, self.tilt))


surfaceSouth = 38 * 2  # 38 panels * 2 m²
surfaceNorth = 36 * 2  # 36 panels * 2 m²

solarSouth = SolarPanels(surface=surfaceSouth, tilt=21)
solarNorth = SolarPanels(surface=surfaceNorth, tilt=-21)

if __name__ == "__main__":

    timezone = pytz.timezone("Europe/Zurich")
    dateT = timezone.localize(datetime.fromisoformat("2020-03-22T00:00:00"))

    df = meanEbhToHourly(158.41, dateT)

    from matplotlib import pyplot as plt

    # plt.plot(hours,heights)
    # plt.show()

    # df = pd.read_csv("data/Crunched/solcastOneDay.csv")
    # df["datetime"] = [datetime.fromisoformat(x[:-1]) for x in df["PeriodStart"]]
    # df = df.drop(df.columns.difference(["Ebh","datetime"]), axis=1)

    powerSouth = [solarSouth.ebhToPower(x, y)
                  for x, y in zip(df["Ebh"], df["datetime"])]
    powerNorth = [solarNorth.ebhToPower(
        x, y.to_pydatetime()) for x, y in zip(df["Ebh"], df["datetime"])]

    powerTotal = [x+y for x, y in zip(powerSouth, powerNorth)]

    print(sum(powerTotal))
