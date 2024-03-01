import pickle
from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np
import sys

def load_and_process_gif(filename):
    with open(filename, 'rb') as file:
        frames = pickle.load(file)
    # Process each frame to change colors
    processed_frames = [change_frame_color(frame) for frame in frames]  # Example: change to red
    return processed_frames

def change_frame_color(frame, black_to_x=(57, 255, 20, 255), white_to_x=(0, 0, 0, 255)):
    black_pixels = (frame[:, :, :3] == [0, 0, 0]).all(axis=2)
    frame[black_pixels] = black_to_x  # Change black pixels to neon green
    white_pixels = (frame[:, :, :3] == [255, 255, 255]).all(axis=2)
    frame[white_pixels] = white_to_x  # Change white pixels to black

    return frame

# Make sure to update the rest of your code to use the updated `change_frame_color` function

current_frame = 0

# Display function
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    frame = frames[current_frame]
    glDrawPixels(frame.shape[1], frame.shape[0], GL_RGBA, GL_UNSIGNED_BYTE, frame)
    glutSwapBuffers()

# Timer function to control frame rate
def update(value):
    global current_frame
    current_frame = (current_frame + 1) % len(frames)
    glutPostRedisplay()
    glutTimerFunc(100, update, 0)  # Adjust the 100ms delay to speed up/slow down

# Keyboard event handler for closing the window
def keyboard(key, x, y):
    if key == b'\x1b':  # ESC key
        sys.exit()

# Initialize OpenGL
def init_opengl(width, height):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"Pixelated GIF Animation")
    glutDisplayFunc(display)
    glutTimerFunc(100, update, 0)  # Start the timer for the first time
    glutKeyboardFunc(keyboard)  # Register the keyboard function
    glClearColor(0.0, 0.0, 0.0, 1.0)

if __name__ == "__main__":
    filename = "file_animation.pkl"  # Update this path
    frames = load_and_process_gif(filename)
    init_opengl(frames[0].shape[1], frames[0].shape[0])
    glutMainLoop()
