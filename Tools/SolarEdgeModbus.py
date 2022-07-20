import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
import solaredge_modbus as smdb
from secret import solar_edge_ip, solar_edge_port
from Tools.Console import log

def CallModbus():
    inv = smdb.Inverter(host=solar_edge_ip,port=solar_edge_port)
    if(inv.connect()):
        try:
            meter = inv.meters()["Meter1"]
            
            solarPower = round(inv.read("power_ac")["power_ac"] * 10 ** inv.read("power_ac_scale")["power_ac_scale"])
            gridPower = round(meter.read("power")["power"] * 10 ** meter.read("power_scale")["power_scale"])
        except KeyError:
            log("Error keyerror")
            inv.disconnect()
            return None
        housePower = solarPower - gridPower
        
        inv.disconnect()
        meter.disconnect()
        
        #print(f"Solar: {solarPower / 1000} kWh\tGrid: {gridPower / 1000} kWh\tHouse: {housePower / 1000} kWh")
        
        return {'solar':solarPower, 'grid':gridPower, 'house':housePower}
    else:
        log("Inverter unreachable")
        inv.disconnect()
            
    return None
    
if __name__=="__main__":
    CallModbus()