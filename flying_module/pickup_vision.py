import sys
import os
import cv2

import logging
import sys
import time
import numpy as np
import random
from threading import Event, Thread

import flying_utils_hardcode

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils import uri_helper
# Add vision_module to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'vision_module'))

from vision_interface import VisionInterface

###################### Purpose of Script ####################################################
'''
This script is writtent to pick up a block and place it at another location. All coordinates are hard-coded.
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

def move_block(vision_interface, commander, block_location_set, block_location, dropoff_location_set, dropoff_location, flight_velocities):
    flying_utils_hardcode.takeoff_go_to(commander)
    while not vision_interface.get_pickup_status():
        flying_utils_hardcode.pickup_block(commander, block_location_set, block_location, flight_velocities[0])
    vision_interface.reset_block_picked()
    commander.go_to(0,0,0.75,flight_velocities[1])
    time.sleep(4)
    flying_utils_hardcode.dropoff_block(commander, dropoff_location_set, dropoff_location, flight_velocities[0])
    time.sleep(2)
    flying_utils_hardcode.land_ground(commander, LAND_VELOCITY)

def vision_background(vision_interface):
    while True:
        vision_interface.process_scene()
        pickups = vision_interface.check_pickups()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def main():
    model_path = r'C:/Users/aksha/OneDrive/Desktop/Desktop/Spring 2024/Research/CrazyConstruct/vision_module/best.pt'  # Path to your YOLO model
    vision_interface = VisionInterface(model_path)
    # Start the vision processing in a background thread
    vision_thread = Thread(target=vision_background, args=(vision_interface,))
    vision_thread.start()

    URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

    
    block_location_set = [-0.15,0.15,0.1] 
    block_location = [-0.15,0.15,0.03]
    dropoff_location_set = [-0.15,0.25,0.1]
    dropoff_location = [-0.15,0.25,0.03]
    flight_velocities = [0.05, 0.2]
    deck_attached_event = Event()
    logged_data = []

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
        move_block(vision_interface, commander, block_location_set, block_location, dropoff_location_set, dropoff_location, flight_velocities)
    vision_interface.scene_processor.cap.release()
    cv2.destroyAllWindows()

######################## Main ##############################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    TAKEOFF_HEIGHT = 0.5
    TAKEOFF_VELOCITY = 0.2
    LAND_VELOCITY = 0.1
    num_cycles = 3
    charging_pad_loc = [0.6,0.46] #landing point 
    main()