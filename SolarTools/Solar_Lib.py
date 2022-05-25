from datetime import datetime, timedelta
import pytz
import pandas as pd
from math import radians
from cmath import sin
from pysolar.solar import get_altitude
import pandas as pd
import numpy as np
from pvlib.solarposition import get_solarposition


def Gti(Ghi, zenith, tilt):
    zenith = radians(zenith)
    tilt = radians(tilt)
    gti = Ghi * sin(zenith + tilt).real
    if gti < 0:
        gti = 0
    return gti


def dailyGhiToHourly(Ghi, date):
    zenithsDateT = np.arange(
        date, date + timedelta(hours=24), timedelta(hours=1), dtype='datetime64')

    zeniths = (90 - get_solarposition(zenithsDateT, 47, 7.02)[
        "zenith"].clip(-90, 90)).tolist()
    factors = [x * (1/sum(zeniths)) for x in zeniths]
    GhiHourly = [f * Ghi for f in factors]
    df = pd.DataFrame(
        {"datetime": zenithsDateT, "Ghi": GhiHourly, "zenith": zeniths}
    )

    return df


def ghiToPower(Ghi, date):

    df = dailyGhiToHourly(Ghi, date)

    powerSouth = [solarSouth.GhiToPower(x, y)
                  for x, y in zip(df["Ghi"], df["zenith"])]
    powerNorth = [solarNorth.GhiToPower(
        x, y) for x, y in zip(df["Ghi"], df["zenith"])]
    return sum(powerSouth + powerNorth)


class SolarPanels:

    def __init__(self, surface, tilt, efficiency=0.2017, lat=47, lon=7.02) -> None:
        self.surface = surface
        self.tilt = tilt
        self.efficiency = efficiency
        self.lat = lat
        self.lon = lon

    def power(self, gti):
        return self.surface * gti * self.efficiency

    def GhiToPower(self, Ghi, zenith):
        return self.power(Gti(Ghi, zenith, self.tilt))


surfaceSouth = 38 * 2  # 38 panels * 2 m²
surfaceNorth = 36 * 2  # 36 panels * 2 m²

solarSouth = SolarPanels(surface=surfaceSouth, tilt=21)
solarNorth = SolarPanels(surface=surfaceNorth, tilt=-21)

if __name__ == "__main__":
    from matplotlib import pyplot as plt

    print(ghiToPower(2000))
