import teslapy

house_lat = 47.0142651
house_lon = 7.0556118

dead_zone = 47.0147642 - house_lat


def is_equal(a, b, tolerance=dead_zone):
    return abs(a - b) < tolerance

def start_charge_if_home():
    with teslapy.Tesla('lenny.boegli@moosvolk.ch') as tesla:
        vehicles = tesla.vehicle_list()
        tesla = vehicles[0]
        
        latest_data = tesla.get_latest_vehicle_data()
        position = (latest_data['drive_state']['latitude'], latest_data['drive_state']['longitude'])
        print(position)
        if latest_data['charge_state']['battery_level'] < 90 and is_equal(position[0], house_lat) and is_equal(position[1], house_lon):
            try:
                tesla.sync_wake_up()
                try:
                    tesla.command('CHANGE_CHARGE_LIMIT', percent=90) # FIXME
                except:
                    pass # If the charge limit is already set to the value, this shitty lib raises an error, wtf
                tesla.command('START_CHARGE')
                print("Charging to 90% Started")
            except teslapy.VehicleError as e:
                print(f"Error starting charge : {e}")
    
def stop_charge_if_home():
    with teslapy.Tesla('lenny.boegli@moosvolk.ch') as tesla:
        vehicles = tesla.vehicle_list()
        tesla = vehicles[0]
        
        latest_data = tesla.get_latest_vehicle_data()
        position = (latest_data['drive_state']['latitude'], latest_data['drive_state']['longitude'])
        print(position)
        if is_equal(position[0], house_lat) and is_equal(position[1], house_lon):
            try:
                tesla.sync_wake_up()
                tesla.command('STOP_CHARGE')
                print("Stopped charge")
            except teslapy.VehicleError as e:
                print(f"Error stopping charge : {e}")
    
    
    # CHANGE_CHARGE_LIMIT
    # START_CHARGE
    # STOP_CHARGE
    
if __name__ == '__main__':
    start_charge_if_home()
    
    