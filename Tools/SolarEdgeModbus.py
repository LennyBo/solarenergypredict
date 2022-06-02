import solaredge_modbus as smdb
import numpy as np

solar_edge_ip = "192.168.0.27"
solar_edge_port = 1502

def CallModbus():
    inv = smdb.Inverter(host=solar_edge_ip,port=solar_edge_port)

    if(inv.connect()):
        meter = inv.meters()["Meter1"]
        
        solarPower = inv.read("power_ac")["power_ac"]
        gridPower = meter.read("power")["power"]
        housePower = solarPower - gridPower
        
        inv.disconnect()
        meter.disconnect()
        
        #print(f"Solar: {solarPower / 1000} kWh\tGrid: {gridPower / 1000} kWh\tHouse: {housePower / 1000} kWh")
        
        return {'solar':solarPower, 'grid':gridPower, 'house':housePower}
    else:
        print("Inverter unreachable")
        inv.disconnect()
        return {'solar':0, 'grid':0, 'house':0}