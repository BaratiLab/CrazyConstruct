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

'''
Definition: Take off from any location and go to specified location.

Input params:
@param: scf - 
@param: TAKEOFF_HEIGHT - The height to take off to.
'''
def takeoff_go_to(commander, TAKEOFF_HEIGHT=1.0, TAKEOFF_VELOCITY=0.2):
    commander.take_off(TAKEOFF_HEIGHT, TAKEOFF_VELOCITY)
    time.sleep(2)
    commander.go_to(0,0,1.0)
    time.sleep(2)

'''
Defintion: Generates a random point and flies to the random point then sleeps there for 15 seconds.
@param: commander- Intitated instance of the PositionHLCommander class.

'''
def goto_randompoint(commander, fly_velocity):
    time.sleep(2)
    randx_pos = random.uniform(-1, 1)
    randy_pos = random.uniform(-1, 1)
    randz_pos = random.uniform(0.3,1)
    commander.go_to(randx_pos, randy_pos, randz_pos, fly_velocity)
    wait_time = random.uniform(1.5, 6)
    time.sleep(wait_time)

'''
Definition: Land from any location to ground.

Input params:
@param: scf - 
@param: LAND_VELOCITY - The speed to land at.
'''
def land_ground(commander, LAND_VELOCITY):
    commander.land(LAND_VELOCITY)

'''
Definition: This picks up the block and slowly lowers the drone
@param: block_location_set:
@param: block_location:
@param: block_set_velocity:
'''
def pickup_block(commander, block_location_set, block_location, block_set_velocity):
    commander.go_to(block_location_set[0],block_location_set[1],block_location_set[2],0.1)
    time.sleep(2)
    commander.go_to(block_location[0],block_location[1],block_location[2], block_set_velocity)
    time.sleep(3)
    commander.go_to(block_location_set[0],block_location_set[1],block_location_set[2], block_set_velocity)
    time.sleep(1)



'''
Definition: This drops of the block at a location
@param: Slowly lowers the block at the drop off location.
'''
def dropoff_block(commander, block_location_set, block_location, block_set_velocity):
    commander.go_to(block_location_set[0],block_location_set[1],block_location_set[2],0.1)
    time.sleep(2)
    commander.go_to(block_location[0],block_location[1],block_location[2], block_set_velocity)
    time.sleep(1)
    commander.go_to(block_location_set[0],block_location_set[1],block_location_set[2], block_set_velocity)
    time.sleep(1)



def move_block(commander, block_location_set, block_location, dropoff_location_set, dropoff_location, flight_velocities):
    takeoff_go_to(commander)
    pickup_block(commander, block_location_set, block_location, flight_velocities[0])
    #goto_randompoint(commander, flight_velocities[1])
    commander.go_to(0.5,0.5,0.6,flight_velocities[1])
    time.sleep(4)
    dropoff_block(commander, dropoff_location_set, dropoff_location, flight_velocities[0])
    commander.go_to(0.5,0.5,0.6,flight_velocities[1])
    time.sleep(2)
    land_ground(commander, LAND_VELOCITY)



######################## Main ##############################################################

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

TAKEOFF_HEIGHT = 0.5
TAKEOFF_VELOCITY = 0.2
LAND_VELOCITY = 0.1
num_cycles = 3
charging_pad_loc = [0.6,0.46]
block_location_set = [0,0.25,0.1]
block_location = [0,0.25,0.04]
dropoff_location_set = [0,0.35,0.1]
dropoff_location = [0,0.35,0.04]
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
        move_block(commander, block_location_set, block_location, dropoff_location_set, dropoff_location, flight_velocities)

