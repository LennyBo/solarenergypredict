import sys
sys.path.append('.')  # Adds parent directory so we can import other modules
import teslapy
import time
from Tools.Console import log
house_lat = 47.0142651
house_lon = 7.0556118

dead_zone = 47.0147642 - house_lat


def is_equal(a, b, tolerance=dead_zone):
    return abs(a - b) < tolerance

def start_charge_if_home():
    with teslapy.Tesla('lenny.boegli@moosvolk.ch') as tesla:
        try:
            vehicles = tesla.vehicle_list()
            tesla = vehicles[0]
            
            latest_data = tesla.get_latest_vehicle_data()
            position = (latest_data['drive_state']['latitude'], latest_data['drive_state']['longitude'])
            if latest_data['charge_state']['battery_level'] < 85 and is_equal(position[0], house_lat) and is_equal(position[1], house_lon):
                try:
                    tesla.sync_wake_up()
                    try:
                        tesla.command('CHANGE_CHARGE_LIMIT', percent=90)
                    except:
                        pass # If the charge limit is already set to the value, this shitty lib raises an error, wtf
                    time.sleep(10)
                    tesla.command('START_CHARGE')
                    log("Charging to 90% Started")
                except teslapy.VehicleError as e:
                    log(f"Error starting charge : {e}")
        except ConnectionError as e:
            log(f"Tesla owner api connection error : {e}")
    
def stop_charge_if_home():
    with teslapy.Tesla('lenny.boegli@moosvolk.ch') as tesla:
        try:
            vehicles = tesla.vehicle_list()
            tesla = vehicles[0]
            
            latest_data = tesla.get_latest_vehicle_data()
            position = (latest_data['drive_state']['latitude'], latest_data['drive_state']['longitude'])
            if is_equal(position[0], house_lat) and is_equal(position[1], house_lon):
                try:
                    tesla.sync_wake_up()
                    try:
                        tesla.command('CHANGE_CHARGE_LIMIT', percent=60)
                    except:
                        pass # If the charge limit is already set to the value, this shitty lib raises an error, wtf
                    time.sleep(10)
                    tesla.command('STOP_CHARGE')
                    log("Stopped charge")
                except teslapy.VehicleError as e:
                    log(f"Error stopping charge : {e}")
        except ConnectionError as e:
            log(f"Tesla owner api connection error : {e}")

def set_charge_limit_if_home(new_limit):
    with teslapy.Tesla('lenny.boegli@moosvolk.ch') as tesla:
        try:
            vehicles = tesla.vehicle_list()
            tesla = vehicles[0]

            latest_data = tesla.get_latest_vehicle_data()
            position = (latest_data['drive_state']['latitude'],
                        latest_data['drive_state']['longitude'])
            current_limit = latest_data['charge_state']['charge_limit_soc']
            if is_equal(position[0], house_lat) and is_equal(position[1], house_lon) and current_limit != new_limit:
                try:
                    tesla.sync_wake_up()
                    try:
                        tesla.command('CHANGE_CHARGE_LIMIT', percent=new_limit)
                    except:
                        pass # If the charge limit is already set to the value, this shitty lib raises an error, wtf
                    log(f"Set charge limit to {new_limit}")
                except teslapy.VehicleError as e:
                    log(f"Error setting charge limit : {e}")
        except ConnectionError as e:
            log(f"Tesla owner api connection error : {e}")
            
    
if __name__ == '__main__':
    set_charge_limit_if_home(65)
    
    