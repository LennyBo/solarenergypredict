from math import radians
from cmath import sin

def ghiToPower(Ghi):
    powerSouth = solarSouth.GhiToPower(Ghi)
    powerNorth = solarNorth.GhiToPower(Ghi)
    return powerSouth + powerNorth


class SolarPanels:

    def __init__(self, surface, tilt, efficiency=0.19, lat=47, lon=7.02) -> None:
        self.surface = surface
        self.tilt = tilt
        self.efficiency = efficiency
        self.lat = lat
        self.lon = lon
        self.tranforCoef = self.surface * sin(radians(self.tilt + self.lat)).real * self.efficiency

    def power(self, gti):
        return self.surface * gti * self.efficiency

    def GhiToPower(self, Ghi):
        return Ghi * self.tranforCoef


surfaceSouth = 38 * 2  # 38 panels * 2 m²
surfaceNorth = 36 * 2  # 36 panels * 2 m²

# print("Surface South:", sin(radians(21+47)).real)
# print("Surface North:", sin(radians(-21+47)).real)
# print("Surface Total:", surfaceSouth * sin(radians(21+47)).real * 0.19 + surfaceNorth * sin(radians(-21+47)).real * 0.19)

solarSouth = SolarPanels(surface=surfaceSouth, tilt=21)
solarNorth = SolarPanels(surface=surfaceNorth, tilt=-21)

if __name__ == "__main__":
    from matplotlib import pyplot as plt

    print(ghiToPower(2000))
