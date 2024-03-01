from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np
from PIL import Image, ImageSequence
import sys
import pickle

def load_and_process_gif(filename):
    frames = []
    img = Image.open(filename)
    for frame in ImageSequence.Iterator(img):
        frame = frame.convert('RGBA')
        flipped_frame = frame.transpose(Image.FLIP_TOP_BOTTOM)
        data = np.array(flipped_frame)
        
        # Adjust color processing logic to include a range of dark pixels
        red, green, blue, alpha = data.T
        
        # Define dark areas (not strictly black, but very dark)
        threshold = 50  # Define a threshold for dark pixels
        dark_areas = (red < threshold) & (green < threshold) & (blue < threshold)
        
        white_areas = (red >= 255) & (green >= 255) & (blue >= 255)
        
        # Convert dark areas to neon green, white areas to black
        data[..., :-1][dark_areas.T] = (0, 0, 0)  
        data[..., :-1][white_areas.T] = (255, 255, 255)   
        
        frames.append(data)
    return frames


frames = load_and_process_gif('file_transfer.gif')
with open('file_animation.pkl', 'wb') as file:
    pickle.dump(frames, file)

