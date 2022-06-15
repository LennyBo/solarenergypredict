import teslapy


with teslapy.Tesla('lenny.boegli@moosvolk.ch') as tesla:
    vehicles = tesla.vehicle_list()
    vehicles[0].sync_wake_up()
    vehicles[0].command('ACTUATE_TRUNK', which_trunk='front')
    vehicles[0].get_vehicle_data()
    print(vehicles[0]['vehicle_state']['car_version'])