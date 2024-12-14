import logging
import sys
import time
import numpy as np
import random
from threading import Event
import json
import apriltag

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils import uri_helper
import flying_utils_hardcode
import llm_manager
import detect_pad_location

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

class LLM_Based_Additive_Manufacturer:
    def __init__(self):
        self.charging_pad_loc = [0.6,0.46] #landing point 
        self.block_location_set_height = 0.1 
        self.block_location_height = 0.03
        self.pickup_location_array = [(0,0),(0,2),(0,4),(1,0),(1,2),(1,4),(2,0),(2,2),(2,4),(3,0),(3,2),(3,4),(4,0),(4,2),(4,4)]
        self.dropoff_set_height = 0.15
        self.dropoff_height = 0.03
        self.flight_velocities = [0.05, 0.2]
        self.logged_data = []
        self.Home_Location = (0, 0, 0)
        self.x0_y0 = None  # X and Y in millimeters from (0,0,0) to the corner of the drop pad
        self.x1_y1 = None # X and Y in millimeters from pad corner to center of first dropoff point
        self.solidworks_measurement = None  # distance from center to center of drop locations in millimeters
        self.rotation_matrix = np.eye(3)

    def get_pad_corner_location(self):
        while True:
            user_input = int(input("Enter 1 for hardcode and 2 for april tag: "))
            if user_input == 1 or user_input == 2:
                break
            else:
                print("Invalid input. Please enter '1' or '2'.")
        if user_input == 1:
            self.x0_y0 = (203.20, 158.75)  # X and Y in millimeters from (0,0,0) to the corner of the drop pad
            self.x1_y1 = (9.525, 9.525) # X and Y in millimeters from pad corner to center of first dropoff point
            self.solidworks_measurement = 19.05  # distance from center to center of drop locations in millimeters
        if user_input == 2:
            relative_position, rotation_matrix = detect_pad_location.main()
            self.x0_y0 = (relative_position[0], relative_position[1])
            self.x1_y1 = (9.525, 9.525) # X and Y in millimeters from pad corner to center of first dropoff point
            self.solidworks_measurement = 19.05
            self.rotation_matrix = rotation_matrix


    def get_xy(self, LLM_coordinate):
        local_x = self.x1_y1[0] + self.solidworks_measurement * LLM_coordinate[0]
        local_y = self.x1_y1[1] + self.solidworks_measurement * LLM_coordinate[1]
        local_point = np.array([local_x, local_y, 0])
        rotated_point = self.rotation_matrix @ local_point
        x = self.x0_y0[0]+rotated_point[0]
        y = self.x0_y0[1]+rotated_point[1]
        x = round(x / 1000, 6)
        y = round(y / 1000, 6)
        drone_xy = (x, y)
        return drone_xy

    def get_coords(self, design):
        title = design['Title']
        coordinates = design['Coordinates']
        return title, coordinates

    def build_design(self, commander, drop_off_positions):
        actual_dropoff_gpt_coords = []
        print(drop_off_positions)
        for i in range(len(drop_off_positions)):
            drone_position = self.get_xy(drop_off_positions[i])
            pickup_location = self.get_xy(self.pickup_location_array[i])
            block_location_set = [pickup_location[0], -pickup_location[1], self.block_location_set_height]
            block_location = [pickup_location[0], -pickup_location[1], self.block_location_height]
            dropoff_location_set = [drone_position[0], drone_position[1], self.dropoff_set_height]
            dropoff_location = [drone_position[0], drone_position[1], self.dropoff_height]
            correct_dropoff_status, dropoff_coords = flying_utils_hardcode.move_block(commander, block_location_set, block_location, dropoff_location_set, dropoff_location, drop_off_positions[i], self.flight_velocities)
            actual_dropoff_gpt_coords.append(dropoff_coords)
            if not correct_dropoff_status:
                commander.go_to(.22,0,0.4,self.flight_velocities[1])
                return False, actual_dropoff_gpt_coords, dropoff_coords, drop_off_positions[i]
        flying_utils_hardcode.land_ground(commander, LAND_VELOCITY)
        return True, actual_dropoff_gpt_coords, dropoff_coords, drop_off_positions[i] 

    def prompt_and_build(self, commander):
        design_status = False
        first_time = True
        while True:
            client = llm_manager.load_api_key()
            if first_time:
                prompt = llm_manager.create_prompt()
                response_text = llm_manager.send_and_receive_prompt(client, prompt)
                first_time = False
                flying_utils_hardcode.takeoff_go_to(commander)
            else:
                prompt = llm_manager.recreate_prompt(prompt, response_text, actual_dropoff_gpt_coords, dropoff_coords, actual_dropoff_coords)
                response_text = llm_manager.send_and_receive_prompt(client, prompt)
            # Load JSON data
            data = json.loads(response_text)
            for design in data['Designs']:
                title, drop_off_positions = self.get_coords(design)
                print(title)
                design_status, actual_dropoff_gpt_coords, dropoff_coords, actual_dropoff_coords = self.build_design(commander, drop_off_positions)
                if not design_status:
                    break
            if design_status:
                break



######################## Main ##############################################################

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

TAKEOFF_HEIGHT = 0.5
TAKEOFF_VELOCITY = 0.2
LAND_VELOCITY = 0.1
deck_attached_event = Event()

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
        llm_builder = LLM_Based_Additive_Manufacturer()
        llm_builder.get_pad_corner_location()
        llm_builder.prompt_and_build(commander)