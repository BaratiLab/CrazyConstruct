# Functions for use in LLM planning and updating

'''
The following imports are needed for the functions contained in this file. 
'''

import matplotlib.pyplot as plt
import numpy as np
import os

grid_value = 10
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
def create_grid_representation(grid_size=(grid_value, grid_value), coordinates=None):
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
    grid_size = grid_value  # Define the grid size
    
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



def plot_coordinates_2(title, list_of_coordinates, list_of_current_coordinates, figure_text, grid_value=10, save=False, folder_path=None):
    grid_size = grid_value  # Define the grid size
    
    # Create the grid with default color value (e.g., 0)
    grid = np.zeros((grid_size, grid_size))
    current_grid = np.zeros((grid_size, grid_size))  # Grid for current coordinates
    
    # Set the color value for the selected coordinates (e.g., 1)
    for x, y in list_of_coordinates:
        grid[y][x] = 1  # Note: row and col are switched here

    for x, y in list_of_current_coordinates:
        current_grid[y][x] = 1  # Note: row and col are switched here
        
    fig, ax = plt.subplots()
    ax.matshow(grid, cmap='plasma', origin='lower', alpha=0.5)  # Background for selected coordinates
    ax.matshow(current_grid, cmap='cool', origin='lower', alpha=0.5)  # Overlay for current coordinates
    
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
            if grid[y][x] == 0 and current_grid[y][x] == 0:
                ax.plot(x, y, 'ro')  # Plot red dots for unselected points
    
    # Add X on the points that are selected
    for x, y in list_of_coordinates:
        ax.text(x, y, 'X', va='center', ha='center', color='black', weight='bold')
    
    # Add O on the points that are current coordinates
    for x, y in list_of_current_coordinates:
        ax.text(x, y, 'O', va='center', ha='center', color='blue', weight='bold')
    
    plt.title(title)
    plt.figtext(0.5, -0.1, figure_text, ha="center", fontsize=9)
    plt.grid(True)

    if save:
        filename = input("Enter the filename to save the figure: ")
        if folder_path:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)  # Create the folder if it doesn't exist
            full_path = os.path.join(folder_path, filename)
        else:
            full_path = filename
        plt.savefig(full_path, bbox_inches='tight', pad_inches=0)

    # Now show the figure
    plt.show()
    



'''Same plotting function but for saving instead'''

def save_plot_coordinates(title, list_of_coordinates, filename=None, folder=None):
    if filename is None:
        raise ValueError("No filename given. Please provide a filename to save the plot.")
        
    if folder:
        # Create the folder if it doesn't exist
        os.makedirs(folder, exist_ok=True)
        # Combine the folder path with the filename
        filepath = os.path.join(folder, filename)
    else:
        filepath = filename

    
    grid_size = grid_value  # Define the grid size
    
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
    plt.savefig(filepath)  # Save the plot if filename is provided
    plt.close()


"""
Creates a prompt for designing a grid layout based on the current coordinates and requested design.

:param current_coordinates: List of coordinates currently marked with 'x' (e.g., [[1, 2], [3, 4]])
:param requested_design: Description of the design to be created (e.g., "An uppercase H")
:return: String representation of the prompt
"""
def create_prompt(current_coordinates, requested_design):

    grid_representation = create_grid_representation(grid_size=(grid_value, grid_value), coordinates=current_coordinates)

    prompt = f"""
A drone is being used to place building blocks on a grid.
Please read all of the following instructions first.

You will be asked to come up with the drop-off locations for the drone that create a specified design.
The origin of the grid is [0,0] in the bottom left corner and the last point is [{grid_value - 1}, {grid_value - 1}] in the top right.
The X axis goes from [0,0] to [{grid_value - 1},0]. The Y axis goes from [0,0] to [0,{grid_value - 1}]. 

You can think of the grid like the pixels of a tv screen, with your job being to decide which pixel to turn on.
The grid currently looks as follows, where "o" is an empty spot (or off pixel) and "x" is a spot that has a existing block (or on pixel):

{grid_representation}


Any existing points marked with "x" has already been chosen and must be incorporated in the design you will create. 
Make sure these pieces then align with one another to create the design in a logical layout.

Only Integer points are allowed.
You can make the design in any orientation that makes sense with the already placed blocks. 
Make sure none of your points exceed the [{grid_value - 1},{grid_value - 1}] index limit. If they do, fix the design.
Make sure the design is legible by thinking step by step as you choose points.
Check the design before confirming it.
If you find an error, retry and then recheck until you find no errors using a step by step approach.
Provide the Title, New Coordinates, Existing Coordinates and your Reasoning in correct JSON format for the design.
The Coordinates should be given in the specific order you would want them executed.
Only return JSON in the structure provided as it needs to be parsed with Python. Do not include any other text or symbols.

Please use the following JSON schema:

{{
    "Design": [
        {{
            "Title": "Title of Design",
            "New Coordinates": [
                [x, y],
                [x, y]
            ],
            "Exisiting Coordinates": [
                [x, y],
                [x, y]
            ],
            "Reasoning": "Your textual reasoning here"
      }}
    ]
}}

You are being asked to design the following: {requested_design}
Think step-by-step.
Make your design now.
"""
    
    return prompt

def get_shapes():
    common_shapes = [
    "donut",
    "circle",
    "square",
    "triangle",
    "rectangle",
    "oval",
    "pentagon",
    "hexagon",
    "octagon",
    "star",
    "cross",
    "arrow",
    "parallelogram",
    "rhombus",
    "trapezoid",
    "kite",
    "heart",
    "crescent",
    "octagram",
    "heptagon",
    "diamond",
    "isosceles triangle",
    "scalene triangle",
    "right triangle",
    "semi-circle",
    "figure-eight",
    "regular pentagram",
    "regular hexagram",
    "right-angled trapezoid",
    "arrowhead",
    "hourglass",
    "wavy line",
    "arrow with rounded ends",
    "rounded rectangle",
    "cloud shape",
    "leaf shape"
]
    return common_shapes



def plot_coordinates_3(title, list_of_coordinates, list_of_current_coordinates, grid_value=10):
    grid_size = grid_value  # Define the grid size
    
    # Create the grid for background (teal/green)
    grid = np.zeros((grid_size, grid_size))
    for x, y in list_of_coordinates:
        grid[y][x] = 1  # Mark the selected coordinates
    
    # Create grids for different categories
    new_coords_grid = np.zeros((grid_size, grid_size))
    current_coords_grid = np.zeros((grid_size, grid_size))
    
    # Populate grids based on the coordinates
    for x, y in list_of_coordinates:
        new_coords_grid[y][x] = 1  # Mark new coordinates
    
    for x, y in list_of_current_coordinates:
        current_coords_grid[y][x] = 1  # Mark current coordinates
    
    fig, ax = plt.subplots()
    
    # Plot the background grid with a color (teal/green)
    ax.matshow(grid, cmap='Greens', origin='lower', alpha=0.5)
    
    # Overlay the new coordinates with a different color
    if np.any(new_coords_grid):  # Check if there are new coordinates to plot
        ax.matshow(new_coords_grid, cmap='Reds', origin='lower', alpha=0.8)
    
    # Overlay the current coordinates with another color
    if np.any(current_coords_grid):  # Check if there are current coordinates to plot
        ax.matshow(current_coords_grid, cmap='Blues', origin='lower', alpha=0.7)
    
    # Move the x-axis to the bottom
    ax.xaxis.set_ticks_position('bottom')
    ax.xaxis.set_label_position('bottom')
    
    # Set ticks and labels
    ax.set_xticks(range(grid_size))
    ax.set_yticks(range(grid_size))
    ax.set_xticklabels(range(grid_size))
    ax.set_yticklabels(range(grid_size))
    
    # Add X on the points that are selected
    for x, y in list_of_coordinates:
        ax.text(x, y, 'X', va='center', ha='center', color='black', weight='bold')
    
    # Add legend
    ax.legend()
    
    plt.title(title)
    plt.grid(True)
    plt.show()









import matplotlib.pyplot as plt
import numpy as np
import os

def plot_correct_coordinates(title, list_of_coordinates, list_of_current_coordinates, figure_text, grid_value=10, save=False, folder_path=None):
    grid_size = grid_value  # Define the grid size
    
    # Create the grid with default color value (e.g., 0)
    grid = np.zeros((grid_size, grid_size))
    current_grid = np.zeros((grid_size, grid_size))  # Grid for current coordinates
    
    # Set the color value for the selected coordinates (e.g., 1)
    for x, y in list_of_coordinates:
        grid[y][x] = 1  # Note: row and col are switched here

    for x, y in list_of_current_coordinates:
        current_grid[y][x] = 1  # Note: row and col are switched here
        
    fig, ax = plt.subplots()
    ax.matshow(grid, cmap='plasma', origin='lower', alpha=0.5)  # Background for selected coordinates
    ax.matshow(current_grid, cmap='cool', origin='lower', alpha=0.5)  # Overlay for current coordinates
    
    # Remove the axis labels, ticks, and spines
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add red dots on points not selected
    for y in range(grid_size):
        for x in range(grid_size):
            if grid[y][x] == 0 and current_grid[y][x] == 0:
                ax.plot(x, y, 'ro')  # Plot red dots for unselected points
    
    # Add X on the points that are selected
    for x, y in list_of_coordinates:
        ax.text(x, y, 'X', va='center', ha='center', color='black', weight='bold')
    
    # Add O on the points that are current coordinates
    for x, y in list_of_current_coordinates:
        ax.text(x, y, 'O', va='center', ha='center', color='blue', weight='bold')
    
    # Remove the title and figure text if not needed
    plt.title('')  # Remove title
    plt.figtext(0.5, -0.1, '', ha="center", fontsize=9)  # Remove figure text

    # Remove the grid if not needed
    plt.grid(False)

    if save:
        filename = input("Enter the filename to save the figure: ")
        if folder_path:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)  # Create the folder if it doesn't exist
            full_path = os.path.join(folder_path, filename)
        else:
            full_path = filename
        plt.savefig(full_path, bbox_inches='tight', pad_inches=0.1)  # Save with minimal padding

    # Show the figure
    plt.show()
