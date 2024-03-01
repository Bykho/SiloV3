import os
import shutil
import json
from ..CA.classifier import run_classification
from datetime import datetime
from multiprocessing import Pool

# Define the global variables for the data.json file path and filter preferences file
DATA_FILE = os.path.join(os.path.expanduser("~/Desktop/SiloV3"), "data.json")
FILTER_PREFERENCES = os.path.join(os.path.dirname(__file__), "filter_preferences.json")

# Define a function to process a single file
def process_file(file_path):
    file_name = os.path.basename(file_path)

    if not file_name.lower().endswith(('.jpg', '.jpeg')):
        print(f"Skipping non-JPEG file: {file_name}")
        return

    # Pull out preferred classes to filter from filter_preferences
    with open(FILTER_PREFERENCES, 'r') as f:
        CLASSES_TO_FILTER = json.load(f)["Classes"]
        #print('Classes to filter:', CLASSES_TO_FILTER)
    
    try:
        # After crawling the file, classify it
        classification_result = run_classification(file_path)
        #print(f"Classification result for {file_name}: {classification_result}")
        
        if classification_result in CLASSES_TO_FILTER:
            # Duplicate the file before moving it
            dest_path = os.path.join(os.path.dirname(file_path), "SiloV3", "SH", file_name)
            shutil.copy2(file_path, dest_path)
            #print(f"File was classified as {classification_result}, preferences are {CLASSES_TO_FILTER}")
            #print(f"Duplicated: {file_name} to {dest_path}")

            # Update data.json file
            update_data_file(file_name, classification_result, dest_path)
        else:
            print(f"File was not classified as per preferences, so it was not duplicated or moved: {file_name}")
    except Exception as e:
        print(f"Error classifying {file_name}: {e}")

# Define a function to update the data.json file
def update_data_file(file_name, classification_result, dest_path):
    try:
        creation_time = datetime.fromtimestamp(os.path.getctime(dest_path)).strftime('%Y-%m-%d %H:%M:%S')
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            data[file_name] = {"classification_result": classification_result, "creation_time": creation_time}
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("An error occurred while updating data file:", e)

# Define a function to crawl through the desktop directory
def crawl_desktop():
    print("Crawling through the desktop directory...")
    # Get the list of all files in the desktop directory
    files_list = []
    for root, dirs, files in os.walk(os.path.expanduser("~/Desktop")):
        for file_name in files:
            files_list.append(os.path.join(root, file_name))
    
    # Use multiprocessing Pool to process files in parallel
    with Pool() as pool:
        pool.map(process_file, files_list)

# Main function to start the crawling process
def main():
    print("Starting the crawling process...")
    crawl_desktop()

if __name__ == "__main__":
    main()
