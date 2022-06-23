from turtle import position
import teslapy

house_lat = 47.0142651
house_lon = 7.0556118

dead_zone = 47.0147642 - house_lat


def is_equal(a, b, tolerance=dead_zone):
    return abs(a - b) < tolerance

with teslapy.Tesla('lenny.boegli@moosvolk.ch') as tesla:
    vehicles = tesla.vehicle_list()
    tesla = vehicles[0]
    latest_data = tesla.get_latest_vehicle_data()
    position = (latest_data['drive_state']['latitude'], latest_data['drive_state']['longitude'])
    print(position)
    if is_equal(position[0], house_lat) and is_equal(position[1], house_lon):
        print("You are at home!")
    else:
        print("You are not at home!")
    
    exit()
    print(vehicles)
    print(vehicles[0]['display_name'] + ' last seen ' + vehicles[0].last_seen() +
          ' at ' + str(vehicles[0]['charge_state']['battery_level']) + '% SoC')
    
    