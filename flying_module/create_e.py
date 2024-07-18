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

def create_e(commander, block_location_set, block_location, dropoff_location_set, dropoff_location, flight_velocities):
    flying_utils_hardcode.takeoff_go_to(commander)
    for i in range(8):
        flying_utils_hardcode.move_block(commander, block_location_set, block_location, dropoff_location_set[i], dropoff_location[i], flight_velocities)
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
dropoff_location_set = [0.03,0.32,0.15]
dropoff_location = [0.03,0.32,0.03]
flight_velocities = [0.05, 0.2]
deck_attached_event = Event()
logged_data = []

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
        #direct_fly_charging_pad(commander, charging_pad_loc, TAKEOFF_HEIGHT, TAKEOFF_VELOCITY, LAND_VELOCITY)
        time.sleep(2)
        create_e(commander, block_location_set, block_location, dropoff_location_set, dropoff_location, flight_velocities)