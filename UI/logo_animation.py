
#THE GAME OF LIFE LOGO SIMULATOR
#Dan Ringness 2024

import glfw
from OpenGL.GL import *
from PIL import Image
import numpy as np

####################################
#EDIT THIS TO CHANGE PARAMETERS: 
image_path = 'silo_bw4.png'  # Replace with your different logo .png/.jpeg
start_mode = 'noise_only' #Include noise at start or not? can be "noise_only" "combined" or "logo_only"
survivability_min = 1  # Lower = more survivable logo: default 2 (ints between 0 and 8) must be less than max
survivability_max = 4 # Higher = more survivable logo: default 4 (ints between 0 and 8) must be greater than min
survivability_rand = 2 # Default is 3 (keep at 2 or 3 recomended), change between 0 and 6 for random behavior
invert_bw = False #invert the pixelmap of the image (default False)
####################################

def image_to_pixelmap(image_path, output_size=(100, 100), threshold=128):
    # Open the image file
    with Image.open(image_path) as img:
        img = img.rotate(-90, expand=True)
        # Resize the image to fit within the specified output size while maintaining aspect ratio
        img.thumbnail(output_size, Image.ANTIALIAS)
        
        # Calculate padding to add to make the image exactly 100x100
        left_padding = (output_size[0] - img.size[0]) // 2
        top_padding = (output_size[1] - img.size[1]) // 2
        right_padding = output_size[0] - img.size[0] - left_padding
        bottom_padding = output_size[1] - img.size[1] - top_padding
        
        # Create a new image with white background and paste the resized image onto it
        new_img = Image.new("L", output_size, "white")
        new_img.paste(img, (left_padding, top_padding))
        
        # Binarize the image based on the threshold
        if invert_bw is False: 
            binary_img = new_img.point(lambda x: 0 if x > threshold else 255, '1')
        elif invert_bw:
            binary_img = new_img.point(lambda x: 255 if x > threshold else 0, '1')

        # Convert the binary image to a NumPy array of 0s and 1s
        pixel_map = np.array(binary_img, dtype=np.uint8)
        
        # Convert 255s to 1s
        pixel_map = np.where(pixel_map > 0, 1, 0)
        
        return pixel_map

# Example usage
pixel_map = image_to_pixelmap(image_path)

def initialize_grid(width, height):
    randomgrid = np.random.choice([0, 1], (width, height))
    comb = np.maximum(randomgrid, pixel_map)
    
    if start_mode == 'combined':
        return comb
    if start_mode == 'noise_only':
        return randomgrid
    if start_mode == 'logo_only':
        return pixel_map

def update_grid(grid, logo_map):
    new_grid = grid.copy()
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            alive_neighbors = np.sum(grid[i-1:i+2, j-1:j+2]) - grid[i, j]

            # Check if the cell is part of the logo and apply custom rules
            if logo_map[i, j] == 1:
                # Custom rules for logo cells
                if alive_neighbors < survivability_min or alive_neighbors > survivability_max:
                    new_grid[i, j] = 0  # Make it more resilient
                elif alive_neighbors == survivability_rand or alive_neighbors == 3:
                    new_grid[i, j] = 1  # Keep alive
            else:
                # Regular Game of Life rules
                if grid[i, j] == 1 and (alive_neighbors < 2 or alive_neighbors > 3):
                    new_grid[i, j] = 0
                elif grid[i, j] == 0 and alive_neighbors == 3:
                    new_grid[i, j] = 1

    return new_grid

def main():
    width, height = 100, 100  # Grid size
    cell_size = 5  # Size of the cell for rendering
    update_interval = .05
    # Initialize glfw
    if not glfw.init():
        return

    window = glfw.create_window(width*cell_size, height*cell_size, "Game of Life", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    grid = initialize_grid(width, height)

    # Loop until the user closes the window
    last_update_time = glfw.get_time()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glColor3f(1.0, 0.45, 0.0)
        glPointSize(7.0)        
        glEnable(GL_BLEND)  # Enable blending
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # Set blending function

        
        current_time = glfw.get_time()
        elapsed_time = current_time - last_update_time

        if elapsed_time >= update_interval:
            # Update the grid
            grid = update_grid(grid, pixel_map)
            last_update_time = current_time


        # Render alive cells
        glBegin(GL_POINTS)
        for i in range(width):
            for j in range(height):
                if grid[i, j] == 1:
                    if pixel_map[i, j] == 1:
                        glColor3f(1.0, 0.45, 0.0)
                    else:
                        glColor3f(0.65, 0.25, 0.0)
                    glVertex2f(i + 0.5, j + 0.5)  # Center the point in the cell
        glEnd()

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
