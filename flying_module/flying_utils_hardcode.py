import logging
import sys
import time
import numpy as np
import random
from threading import Event

###################### Purpose of Script ####################################################
'''
This script is writtent to pick up a block and place it at another location. All coordinates are hard-coded.
'''

####################### Required Functions ##################################################
'''
Definition: Take off from any location and go to specified location.

Input params:
@param: scf - 
@param: TAKEOFF_HEIGHT - The height to take off to.
'''
def is_complete(status):
    while True:
        user_input = input("Enter 'yes' or 'no': ").strip().lower()
        if user_input == 'yes' or user_input == 'no':
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")
    if user_input == 'yes':
        status = True
    else:
        status = False
    return status

'''
Definition: Take off from any location and go to specified location.

Input params:
@param: scf - 
@param: TAKEOFF_HEIGHT - The height to take off to.
'''
def takeoff_go_to(commander, TAKEOFF_HEIGHT=0.5, TAKEOFF_VELOCITY=0.2):
    commander.take_off(TAKEOFF_HEIGHT, TAKEOFF_VELOCITY)
    time.sleep(2)
    commander.go_to(0,0,0.5)
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
    commander.go_to(0.5,0.5,0.5,0.3)
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
    pickup_status = False
    dropoff_status = False
    while not pickup_status:
        pickup_block(commander, block_location_set, block_location, flight_velocities[0])
        pickup_status = is_complete(pickup_status)
    #goto_randompoint(commander, flight_velocities[1])
    commander.go_to(0.5,0,0.4,flight_velocities[1])
    time.sleep(1)
    while not dropoff_status:
        dropoff_block(commander, dropoff_location_set, dropoff_location, flight_velocities[0])
        dropoff_status = is_complete(dropoff_status)
    time.sleep(2)