import solaredge_modbus as smdb

solar_edge_ip = "192.168.0.27"
solar_edge_port = 1502

def CallModbus(max_retries=3):
    inv = smdb.Inverter(host=solar_edge_ip,port=solar_edge_port)
    tries_left = max_retries
    while tries_left:
        tries_left -= 1
        if(inv.connect()):
            try:
                meter = inv.meters()["Meter1"]
                
                solarPower = round(inv.read("power_ac")["power_ac"] * 10 ** inv.read("power_ac_scale")["power_ac_scale"])
                gridPower = round(meter.read("power")["power"] * 10 ** meter.read("power_scale")["power_scale"])
            except KeyError:
                print("Error keyerror")
                inv.disconnect()
                continue
            housePower = solarPower - gridPower
            
            inv.disconnect()
            meter.disconnect()
            
            #print(f"Solar: {solarPower / 1000} kWh\tGrid: {gridPower / 1000} kWh\tHouse: {housePower / 1000} kWh")
            
            return {'solar':solarPower, 'grid':gridPower, 'house':housePower}
        else:
            print("Inverter unreachable")
            inv.disconnect()
            
    return {'solar':0, 'grid':0, 'house':0}
    
if __name__=="__main__":
    CallModbus()