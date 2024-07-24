# Functions for use in LLM planning and updating

'''
The following imports are needed for the functions contained in this file. 
'''

import matplotlib.pyplot as plt
import numpy as np




#Functions

"""
Creates a grid representation with 'x' for specified coordinates and 'o' for all unspecified coordinates.
If no coordinates are specified, the entire grid will be marked with 'o' (such as in the first prompt to the LLM).
Includes labels for the y-axis on the left and the x-axis at the bottom.

:param grid_size: Size of the grid (tuple of two integers, e.g., (5, 5) for a 5x5 grid)
:param coordinates: List of coordinates to be marked with 'x' (e.g., [[1, 2], [3, 4]]). 
                    If None, all positions will be marked with 'o'.
:return: String representation of the grid with axis labels
"""
def create_grid_representation(grid_size=(5, 5), coordinates=None):
    # If coordinates is None, initialize it as an empty list
    if coordinates is None:
        coordinates = []

    # Determine if we should mark specified positions with 'x' or all positions with 'o'
    mark_all_with_o = not coordinates

    # Initialize the grid with 'o'
    grid = [['o' for _ in range(grid_size[0])] for _ in range(grid_size[1])]

    # Mark the specified coordinates with 'x' if coordinates are provided
    if not mark_all_with_o:
        for x, y in coordinates:
            grid[grid_size[1] - 1 - y][x] = 'x'  # Reverse the y-axis to have (0,0) at bottom left

    # Create the string representation
    grid_representation = ""
    for idx, row in enumerate(grid):
        grid_representation += str(grid_size[1] - 1 - idx) + " " + " ".join(row) + "\n"

    # Add bottom x-axis labels
    grid_representation += "  " + " ".join(map(str, range(grid_size[0]))) + "\n"
    
    return grid_representation


'''
plot_coordinates uses matplotlib to create a plot that represetns the real world structure of the blocks. 
This allows a direct comparison of the proposed plan to the real world result in an easier to digest format.

param title: Title of the design
param list_of_coordinates: list of coordinates that needs to be plotted
'''
def plot_coordinates(title, list_of_coordinates):
    grid_size = 5  # Define the grid size
    
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




def create_test_json_prompt(original_prompt, JSON_Output, correct_xy, desired_xy, actual_xy):
    """
    Creates a test JSON prompt based on the provided parameters.

    :param original_prompt: The initial prompt provided to the model.
    :param JSON_Output: The JSON response from the model to the initial prompt.
    :param correct_xy: Coordinates where blocks were correctly placed.
    :param desired_xy: Coordinates where a block was intended to be placed.
    :param actual_xy: Coordinates where a block was actually placed.
    :return: A formatted test JSON prompt string.
    """
    test_json_prompt = f"""
You were previously provided the following prompt: 
START PROMPT 
{original_prompt} 
END PROMPT

Your response to this prompt was the following JSON: 
START RESPONSE 
{JSON_Output} 
END RESPONSE

While executing the coordinates that were previously provided, blocks were correctly placed at {correct_xy}.
However, when trying to place a block at {desired_xy}, it was instead placed at {actual_xy}.

This means there are currently blocks at {correct_xy} and {actual_xy}.

You are now tasked with checking the design and recovering it if possible.

If the design is recoverable by continuing with the current plan in a different order, then
provide the coordinates where blocks still need to be placed in the JSON structure provided.

If the design is not recoverable with the current plan, then try to recover it with a new layout that incorporates the already placed blocks. 
A new layout might mean a different orientation of the design, such as turning the design or laterally shifting it, which is allowed if needed. 
Note that any block that has already been placed cannot be removed and therefore must be used in any new designs.
Make sure your design makes sense. If you do a redesign, then provide the coordinates where blocks still need to be placed in the JSON structure provided.

Make sure to follow the instructions from the original prompt if needed.

If the design is not recoverable at all, set the Title as "Design is not recoverable" and provide no Coordinates.
"""
    return test_json_prompt


