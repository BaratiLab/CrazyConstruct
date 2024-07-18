import logging
import sys
import time
import numpy as np
import random
from threading import Event

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils import uri_helper
import flying_utils_hardcode

###################### Purpose of Script ####################################################
'''
Create E from hard code coords.
'''

####################### Required Functions ##################################################
def log_pos_callback(timestamp, data, logconf):
    print(data)

'''
Definition: Check if lighthouse deck is attached and eveything works well before flight.

Input Params:
@param: value_str - The type of deck attached to the drone.

Ouput Params:
None
'''
def param_deck_lighthouse(_, value_str):
    value = int(value_str)
    if value:
        deck_attached_event.set()
        print('Deck is attached!')
    else:
        print('Deck is NOT attached!')


def get_xy(LLM_coordinate):
    x = x0_y0[0] + x1_y1[0] + solidoworks_measurement * LLM_coordinate[0]
    y = x0_y0[1] + x1_y1[1] + solidoworks_measurement * LLM_coordinate[1]
    x = round(x / 1000, 6)
    y = round(y / 1000, 6)
    drone_xy = (x, y)
    return drone_xy

    

def create_e(commander, block_location_set, block_location, drop_off_positions, dropoff_set_height, dropoff_height, flight_velocities):
    flying_utils_hardcode.takeoff_go_to(commander)
    for i in range(8):
        drone_position = get_xy(drop_off_positions[i])
        dropoff_location_set = [drone_position[0], drone_position[1], dropoff_set_height]
        dropoff_location = [drone_position[0], drone_position[1], dropoff_height]
        flying_utils_hardcode.move_block(commander, block_location_set, block_location, dropoff_location_set, dropoff_location, flight_velocities)
    flying_utils_hardcode.land_ground(commander, LAND_VELOCITY)

######################## Main ##############################################################

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

TAKEOFF_HEIGHT = 0.5
TAKEOFF_VELOCITY = 0.2
LAND_VELOCITY = 0.1
num_cycles = 3
charging_pad_loc = [0.6,0.46] #landing point 
block_location_set = [0.30,0.16,0.1] 
block_location = [0.30,0.16,0.03]
dropoff_set_height = 0.15
dropoff_height = 0.03
flight_velocities = [0.05, 0.2]
deck_attached_event = Event()
logged_data = []
Home_Location = (0, 0, 0)
x0_y0 = (203.20, 254)  # X and Y in millimeters from (0,0,0) to the corner of the drop pad
x1_y1 = (9.525, 9.525) # X and Y in millimeters from pad corner to center of first dropoff point
solidoworks_measurement = 19.05  # distance from center to center of drop locations in millimeters

logging.basicConfig(level=logging.ERROR)

if __name__ == '__main__':

    cflib.crtp.init_drivers()
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        scf.cf.param.add_update_callback(group='deck', name='bcLighthouse4',
                                         cb=param_deck_lighthouse)
        time.sleep(1)

        if not deck_attached_event.wait(timeout=5):
            print('No flow deck detected!')
            sys.exit(1)
        
        commander = PositionHlCommander(scf)
        drop_off_positions = [(0,0),(1,0),(2,0),(3,0),(4,0),(0,1),(2,1),(4,1)]
        #direct_fly_charging_pad(commander, charging_pad_loc, TAKEOFF_HEIGHT, TAKEOFF_VELOCITY, LAND_VELOCITY)
        time.sleep(2)
        create_e(commander, block_location_set, block_location, drop_off_positions, dropoff_set_height, dropoff_height, flight_velocities)