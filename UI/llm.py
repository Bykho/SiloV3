import sys
import numpy as np
from openai import OpenAI
from PIL import Image
import pickle
from OpenGL.GL import *
import OpenGL.GLUT as GLUT
from PyQt5.QtCore import Qt, QTimer, QStringListModel
from PyQt5.QtGui import QFont, QIcon, QOpenGLContext, QPixmap, QImage, QColor, QPainter
from PyQt5.QtWidgets import (QSplitter, QApplication, QFrame, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QCompleter, QHBoxLayout, QStackedLayout, QOpenGLWidget, QScrollArea, QGridLayout)

#from ..misc.config import OPENAI_API_KEY, ASSISTANT_ID
OPENAI_API_KEY = "sk-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"
ASSISTANT_ID = "asst_IYTjEetTeZYOQfZe3AL8AemY"

PM = None
blues = [[0.0, 0.569, 0.996], [0.0, 0.216, 0.9], [0.0, 0.255, 0.780]] 
oranges = [[1, 0.376, 0],[1, 0.271, 0], [0.929, 0.404, 0]]
greens = [[0.0, 1.0, 0.0], [0.0, 0.8, 0.0], [0.0, 0.6, 0.0]]

style = 'orange' #enter blue green or orange

def load_and_process_gif(filename):
    with open(filename, 'rb') as file:
        frames = pickle.load(file)
    processed_frames = [change_frame_color(frame) for frame in frames]
    return processed_frames

def change_frame_color(frame):
    global style
    if style == 'blue': 
        black_pixels = (frame[:, :, :3] == [0, 0, 0]).all(axis=2)
        frame[black_pixels] = (0, 80, 255, 255)
    if style == 'orange':
        black_pixels = (frame[:, :, :3] == [0, 0, 0]).all(axis=2)
        frame[black_pixels] = (255, 85, 0, 255)
    else: 
        black_pixels = (frame[:, :, :3] == [0, 0, 0]).all(axis=2)
        frame[black_pixels] = (57, 255, 20, 255)
        white_pixels = (frame[:, :, :3] == [255, 255, 255]).all(axis=2)
        frame[white_pixels] = (0, 0, 0, 255)

    return frame

STYLESHEETS = {
    'orange': """
        QWidget {
            font-family: 'Consolas', 'Courier New', monospace; /* Using a monospace font for that hacker feel */
            font-size: 14px;
            color: #FF7300; /* Burnt orange text */
            background-color: #000000; /* Black background */
        }
        QLineEdit {
            border: 2px solid #FF7300; /* Burnt orange border */
            border-radius: 5px; /* Slightly rounded corners for a modern touch */
            padding: 5px;
            background-color: #121212; /* Slightly off-black background for depth */
            color: #FF8C00; /* Burnt orange text */
        }
        QLineEdit:hover, QLineEdit:focus {
            border: 2px solid #FF8E00; /* Brighter orange on hover/focus */
        }
        QPushButton {
            border: 2px solid #FF7300;
            border-radius: 5px;
            padding: 5px;
            background-color: #121212;
            color: #FF8C00;
        }
        QPushButton:hover {
            border-color: #FFA500;
            background-color: #202020; /* Darker background on hover for depth */
        }
        QLabel {
            qproperty-alignment: 'AlignLeft';
        }
        QListView {
            font-family: 'Consolas', 'Courier New', monospace; /* Using a monospace font for that hacker feel */
            font-size: 14px;
            selection-background-color: #FF8C00; /* Burnt orange background for selected item */
            selection-color: #000000; /* Black text for selected item */
        }
    """,
    'blue': """
        QWidget {
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12px;
            color: #0091FE;
            background-color: #000000;
        }
        QLineEdit, QPushButton, QLabel {
            border: 2px solid #0037E6;
            border-radius: 5px;
            padding: 5px;
            background-color: #000000;
            color: #0091FE;
        }
        QLineEdit:hover, QLineEdit:focus, QPushButton:hover {
            border: 2px solid #0091FE;
        }
        QPushButton {
            background-color: #1A1A1A;
        }
        QListView {
            font-family: 'Consolas', 'Courier New', monospace; /* Using a monospace font for that hacker feel */
            font-size: 14px;
            selection-background-color: #0091FE; /* Burnt orange background for selected item */
            selection-color: #000000; /* Black text for selected item */
        }
    """,
    'green': """
        QWidget {
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12px;
            color: #33FF00; /* Bright neon green for text */
            background-color: #000000; /* Black background */
        }
        QLineEdit, QPushButton, QLabel {
            border: 2px solid #3ccf00; /* Slightly lighter neon green for borders */
            border-radius: 5px;
            padding: 5px;
            background-color: #000000; /* Dark grey for input, button, and label backgrounds */
            color: #33FF00; /* Bright neon green for text */
        }
        QLineEdit:hover, QLineEdit:focus, QPushButton:hover {
            border: 2px solid #33FF00; /* Bright neon green for hover/focus borders */
        }
        QPushButton {
            background-color: #292929; /* Darker grey for button background */
        }
        QListView {
            font-family: 'Consolas', 'Courier New', monospace; /* Using a monospace font for that hacker feel */
            font-size: 14px;
            selection-background-color: #33FF00; /* Neon green background for selected item */
            selection-color: #000000; /* Black text for selected item */
        }
"""
}

class OpenGLWidget(QOpenGLWidget):
    global style
    def __init__(self, parent=None):
        super(OpenGLWidget, self).__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(60)  # Update interval in milliseconds
        self.grid = None
        self.pixel_map = None
        self.initialize_game_parameters()

    def initialize_game_parameters(self):
        # Load and process the image, initialize the grid here
        self.pixel_map = self.image_to_pixelmap('silo_bw4.png')
        self.grid = self.initialize_grid(100, 100, self.pixel_map)

        # Additional initialization based on your simulator parameters

    def image_to_pixelmap(self, image_path, output_size=(100, 100), threshold=128, invert_bw=False):
        global PM
        # Open the image file
        with Image.open(image_path) as img:
            img = img.rotate(-90, expand=True)
            # Resize the image to fit within the specified output size while maintaining aspect ratio
            img.thumbnail(output_size, Image.LANCZOS)  # Changed Image.ANTIALIAS to Image.LANCZOS
            
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
            PM = pixel_map
            return pixel_map


    def initialize_grid(self, width, height, pixel_map):
        randomgrid = np.random.choice([0, 1], (width, height))
        randomgrid = np.random.choice([0, 1], size=(width, height), p=[.95, .05])
        comb = np.maximum(randomgrid, pixel_map)
        return randomgrid

    def update_grid(self, grid, logo_map):
        new_grid = grid.copy()
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                alive_neighbors = np.sum(grid[i-1:i+2, j-1:j+2]) - grid[i, j]

                # Check if the cell is part of the logo and apply custom rules
                if logo_map[i, j] == 1:
                    # Custom rules for logo cells
                    if alive_neighbors < 1 or alive_neighbors > 7:
                        new_grid[i, j] = 0  # Make it more resilient
                    elif alive_neighbors == 2 or alive_neighbors == 3:
                        new_grid[i, j] = 1  # Keep alive
                else:
                    # Regular Game of Life rules
                    if grid[i, j] == 1 and (alive_neighbors < 2 or alive_neighbors > 3):
                        new_grid[i, j] = 0
                    elif grid[i, j] == 0 and alive_neighbors == 3:
                        new_grid[i, j] = 1

        return new_grid

    def initializeGL(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.0, 0.0, 0.0, 1.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        global blues
        global oranges
        global greens

        # Optionally set the coordinate system to match the grid size
        glOrtho(0, 100, 0, 100, -1, 1)
        
        # Update the grid for the next frame
        self.grid = self.update_grid(self.grid, self.pixel_map)
        
        # Set the color for drawing live cells
        glColor3f(1.0, 0.45, 0.0)
        glPointSize(5.0) 
        # Draw the cells
        glBegin(GL_POINTS)  # Start drawing points
        for i in range(100):  # Assuming a 100x100 grid
            for j in range(100):
                if self.grid[i, j] == 1:
                    if PM[i, j] == 1:
                        if style == 'blue':
                            glColor3f(0, 0.686, 1)
                        if style == 'green':
                            glColor3f(0.427, 1, 0.192)
                        if style == 'orange':
                            glColor3f(1, 0.525, 0)  
                    else:
                        c = np.random.choice([0,1,2])
                        if style == 'blue':
                            glColor3f(blues[c][0], blues[c][1], blues[c][2])
                        if style == 'green':
                            glColor3f(greens[c][0], greens[c][1], greens[c][2])
                        if style == 'orange':
                            glColor3f(oranges[c][0], oranges[c][1], oranges[c][2])
                        #glColor3f(0.65, 0.25, 0.0)
                    glVertex2f(i + 0.5, j + 0.5)   # Draw cell; +0.5 to center in cell
        glEnd()  # End drawing points
        
        # Force OpenGL to start processing queued commands
        glFlush()


    def resizeGL(self, width, height):
        # Prevent division by zero
        if height == 0:
            height = 1
        
        aspectRatio = width / height
        zoomFactor = 0.5  # Example zoom factor; less than 1 to zoom in, greater than 1 to zoom out

        # Set the viewport to cover the new window
        glViewport(0, 0, width, height)

        # Reset the coordinate system before modifying
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # Adjust the clipping volume
        if width >= height:
            # Landscape or square window
            glOrtho(-aspectRatio * zoomFactor, aspectRatio * zoomFactor, -zoomFactor, zoomFactor, -1.0, 1.0)
        else:
            # Portrait window
            glOrtho(-zoomFactor, zoomFactor, -zoomFactor / aspectRatio, zoomFactor / aspectRatio, -1.0, 1.0)

        # Switch back to model view matrix mode
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

class FileAnimation(QOpenGLWidget):
    global style
    def __init__(self, parent=None):
        super(FileAnimation, self).__init__(parent)
        self.frames = load_and_process_gif("file_animation.pkl")
        self.current_frame = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(100)  # Adjust the 100ms delay to speed up/slow down

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        frame = self.frames[self.current_frame]
        glDrawPixels(frame.shape[1], frame.shape[0], GL_RGBA, GL_UNSIGNED_BYTE, frame)

    def updateFrame(self):
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.update()

    
    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
    
class SimpleApp(QWidget):
    global style
    def __init__(self):
        super().__init__()
        self.initializeUI()

    def initializeUI(self):
        self.setWindowTitle('Desktop GPT')
        self.setGeometry(0, 0, 1200, 600)  # Increased width to accommodate OpenGL widget
        self.setStyleSheet(STYLESHEETS[style])

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        self.openglWidget = OpenGLWidget(self)
        left_layout.addWidget(self.openglWidget)
        
        # Input Method 1: Plain Text with Suggestions
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText('Enter your request')
        self.text_input.setFont(QFont('Consolas', 12))
        self.suggestions = QStringListModel()
        self.suggestions.setStringList(["Move", "Copy", "Paste", "Find", "Delete", "Rename", "Download", "Upload", "Install", "Uninstall", "Update", "Backup", "Restore", "Configure", "Secure", "Monitor", "Optimize", "Schedule", "Access", "Encrypt"])
        self.completer = QCompleter()
        self.completer.setModel(self.suggestions)
        popup = self.completer.popup()
        popup.setStyleSheet(STYLESHEETS[style])
        self.text_input.setCompleter(self.completer)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity(False))
        left_layout.addWidget(self.text_input)
        
        # Response Label
        self.response_label = QLabel('Response will appear here...', self)
        self.response_label.setWordWrap(True)
        self.response_label.setStyleSheet("margin-top: 20px;")
        left_layout.addWidget(self.response_label)

        # Enter Button (common for both methods)
        self.button = QPushButton('Enter', self)
        self.button.clicked.connect(self.on_button_clicked)
        self.button.setFont(QFont('Arial', 12))
        left_layout.addWidget(self.button)
        

        # Grid of File Images
        imageGridLayout = QGridLayout()
        imageGridLayout.setSpacing(2)  # Reduce the spacing to make images closer together
        imageGridLayout.setContentsMargins(2, 2, 2, 2)  # Reduce overall grid margin
        image_path = 'file.png'

        file_count, file_data = read_data_json(data.json)
        positions = turn_file_count_to_grid(file_count)
        desktop_data = apply_file_data(file_data, positions)
        originalImage = QImage(image_path)

        def read_data_json(data):
            #accepts data.json
            #run through the json file incrementing count
            #run through json extracting sub-detail and appending to a a results list
            file_count = 0
            file_data = []
            for file in data:
                file_count += 1
                file_data.append(file.flatten()[1:])
            
            return file_count, file_data
        
        def apply_file_data(file_data, positions):
            Desktop = []
            file_data_index = 0

            #Check how indexing works here
            for i, val in enumerate(range(len(positions))):
                Desktop.append([])
                for j in range(len(positions)):
                    Desktop[i].append(file_data[file_data_index])
                    file_data_index += 1
            return Desktop
        
        def turn_file_count_to_grid(count):

            if count < 5:
                side = int(np.log(count))
                locations = [(i, j) for i in range(side) for j in range(side)]
                #check indices and zero indexing here
                while len(locations) * len(locations[0]) < count:
                    locations.append([(len(locations), j) for j in range(side)])

            else:
                width = 4
                if count%width == 0:
                    depth = count / width
                else:
                    depth = int(count/width) + 1
                locations = [(i, j) for i in range(width) for j in range(depth)]
            
            return locations

        

        # Tint the image based on style
        if style == 'blue':
            tintedImage = self.tintImage(originalImage, QColor(0, 80, 255))  
        elif style == 'orange':  # Use elif for better efficiency
            tintedImage = self.tintImage(originalImage, QColor(255, 85, 0))  
        elif style == 'green':
            tintedImage = self.tintImage(originalImage, QColor(57, 255, 20))  

        for pos in positions:
            label = QLabel()
            pixmap = QPixmap.fromImage(tintedImage)

            #here we can add the descriptions

            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("background: transparent; border: none;")  # Remove boxes around images
            imageGridLayout.addWidget(label, *pos)

        # Widget to hold the grid layout
        imageGridWidget = QWidget()
        imageGridWidget.setLayout(imageGridLayout)
        # Add the grid layout to the main vertical layout
        right_layout.addWidget(imageGridWidget)

        # Add the OpenGL widget to the main layout, to the right of the existing UI elements
        self.fileGIF = FileAnimation(self)
        right_layout.addWidget(self.fileGIF)

        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 3)

        self.setLayout(main_layout)


    def callGPT(self, user_prompt):
        # Securely set your OpenAI API key
        client = OpenAI(api_key= OPENAI_API_KEY )
        assistant = client.beta.assistants.retrieve(assistant_id= ASSISTANT_ID)
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content= str(user_prompt)
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )

        return messages
        '''
        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": str(user_prompt)}
        ]
        )

        return completion.choices[0].message.content
        '''
    def on_button_clicked(self):
        user_text = self.text_input.text()
        
        # Now actually calling the GPT function to get a response
        gpt_response = self.callGPT(user_text)
        response = f"{gpt_response}"
        self.response_label.setText(response)
        self.response_label.setStyleSheet(STYLESHEETS[style])

    def tintImage(self, image, color):
        sourceImage = image.convertToFormat(QImage.Format_ARGB32)
        tintedImage = QImage(sourceImage.size(), QImage.Format_ARGB32)
        tintedImage.fill(Qt.transparent)  # Start with a transparent image

        painter = QPainter(tintedImage)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.drawImage(0, 0, sourceImage)  # Draw the original image as the base

        # Set the composition mode to apply the tint color to white areas
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        # The tint color is applied here. It replaces the source's color (white in this case) with the tint color.
        painter.fillRect(tintedImage.rect(), color)

        painter.end()
        return tintedImage

def main():
    app = QApplication(sys.argv)
    window = SimpleApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
