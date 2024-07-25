import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import ast
from pathlib import Path
import json
import numpy as np

def plot_coordinates(title, list_of_coordinates):
    grid_size = 25  # Define the grid size
    
    # Create the grid with default color value (e.g., 0)
    grid = np.zeros((grid_size, grid_size))
    
    # Set the color value for the selected coordinates (e.g., 1)
    for x, y in list_of_coordinates:
        grid[y][x] = 1  # Note: row and col are switched here
    
    fig, ax = plt.subplots()
    cax = ax.matshow(grid, cmap='plasma', origin='lower')
    
    # Move the x-axis to the bottom
    ax.xaxis.set_ticks_position('bottom')
    ax.xaxis.set_label_position('bottom')
    
    # Set ticks and labels
    ax.set_xticks(range(grid_size))
    ax.set_yticks(range(grid_size))
    ax.set_xticklabels(range(grid_size))
    ax.set_yticklabels(range(grid_size))
    
    # Add red dots on points not selected
    for y in range(grid_size):
        for x in range(grid_size):
            if grid[y][x] == 0:
                ax.plot(x, y, 'ro')  # Plot red dots for unselected points
    
    # Add X on the points that are selected
    for y in range(grid_size):
        for x in range(grid_size):
            if grid[y][x] == 1:
                ax.text(x, y, 'X', va='center', ha='center', color='Black', weight='bold')
    
    plt.title(title)
    plt.grid(True)
    plt.show()


def load_api_key():
    # Specify the path to the .env file
    env_path = Path(r'C:\Users\CrazyFlie\Documents\Nonuploadable_Git\.env')
    lab_env_path = Path(r'/home/crazyflie/Documents/MAIL_projects/env')
    # Load the .env file
    load_dotenv(dotenv_path=lab_env_path)

    # Get the OpenAI API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI(
        api_key=api_key
    )
    return client

def create_prompt():
    prompt = """
    A drone us being used to place building blocks on a grid.
    You are being asked to come up with the drop off locations for the drone that create a specified design.
    The origin of the grid is [0,0] in the bottom left corner and the last point is [5,5] in the top right.
    The X axis goes from [0,0] to [5,0]. The Y axis goes from [0,0] to [0,5].
    Make sure none of your points exceed the [5,5] index limit. If they do, fix the design.
    Only Integers are allowed.
    Please provide the Title and Coordinates in correct JSON format for the Design of a smiley face.
    The Coordinates should be given in the specific order you would want them executed.
    Make sure your design makes sense and would be legible.
    Make sure the design is legible by thinking step by step as you choose points.
    Check the design before confirming it, such as for legibility and index limit of 5.
    If it is wrong, redo the design and then recheck until you find no errors using a step by step approach.
    Only return the JSON in the strucuture provided as it needs to be parsed with Python. Do not include any other text or symbols.
    Please use the following structure:
    {
        "Designs": [
            {
                "Title": "Title of Design",
                "Coordinates": [
                    [x, y],
                    [x, y]
                ],
                "Reasoning": "Your textual reseasoning here"
        }
        ]
    }
    """
    return prompt

def recreate_prompt(actual_dropoff_gpt_coords, dropoff_coords, actual_dropoff_coords):
    pass    

def send_and_receive_prompt(client, prompt):
    # Send the request to OpenAI using the new ChatCompletion method
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format = {"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],   
    )
    response_text = response.choices[0].message.content
    return response_text