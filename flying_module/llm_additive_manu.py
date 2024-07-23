import logging
import sys
import time
import numpy as np
import random
from threading import Event
import json

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils import uri_helper
import flying_utils_hardcode
import llm_manager

###################### Purpose of Script ####################################################
'''
create letter using LLM
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

def get_coords(design):
    title = design['Title']
    coordinates = design['Coordinates']
    return title, coordinates

def build_design(commander, block_location_set_height, block_location_height, pickup_location_array, drop_off_positions, dropoff_set_height, dropoff_height, flight_velocities):
    flying_utils_hardcode.takeoff_go_to(commander)
    print(drop_off_positions)
    for i in range(len(drop_off_positions)):
        drone_position = get_xy(drop_off_positions[i])
        pickup_location = get_xy(pickup_location_array[i])
        block_location_set = [pickup_location[0], -pickup_location[1], block_location_set_height]
        block_location = [pickup_location[0], -pickup_location[1], block_location_height]
        dropoff_location_set = [drone_position[0], drone_position[1], dropoff_set_height]
        dropoff_location = [drone_position[0], drone_position[1], dropoff_height]
        flying_utils_hardcode.move_block(commander, block_location_set, block_location, dropoff_location_set, dropoff_location, flight_velocities)
    flying_utils_hardcode.land_ground(commander, LAND_VELOCITY)

def prompt_and_build(commander, block_location_set, block_location, pickup_location_array, dropoff_set_height, dropoff_height, flight_velocities):
    client = llm_manager.load_api_key()
    prompt = llm_manager.create_prompt()
    response_text = llm_manager.send_and_receive_prompt(client, prompt)
    # Load JSON data
    data = json.loads(response_text)
    for design in data['Designs']:
        title, drop_off_positions = get_coords(design)
        print(title)
        build_design(commander, block_location_set, block_location, pickup_location_array, drop_off_positions, dropoff_set_height, dropoff_height, flight_velocities)



######################## Main ##############################################################

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

TAKEOFF_HEIGHT = 0.5
TAKEOFF_VELOCITY = 0.2
LAND_VELOCITY = 0.1
num_cycles = 3
charging_pad_loc = [0.6,0.46] #landing point 
block_location_set = 0.1 
block_location = 0.03
pickup_location_array = [(0,0),(2,0),(4,0),(0,1),(2,1),(4,1),(0,2),(2,2),(4,2),(0,3),(2,3),(4,3),(0,4),(2,4),(4,4)]
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
        #direct_fly_charging_pad(commander, charging_pad_loc, TAKEOFF_HEIGHT, TAKEOFF_VELOCITY, LAND_VELOCITY)
        time.sleep(2)
        prompt_and_build(commander, block_location_set, block_location, pickup_location_array, dropoff_set_height, dropoff_height, flight_velocities)