import os
import shutil
import json
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../CA')))
from classifier import run_classification
from datetime import datetime
import signal
import sys
import psutil

# Define the global variables
DATA_FILE = os.path.join(os.path.expanduser("~/Desktop/SiloV3"), "data.json")
FILTER_PREFERENCES = os.path.join(os.path.dirname(__file__), "filter_preferences.json")
LOCK_FILE = "/tmp/silov3_daemon.lock"

class FileHandler(FileSystemEventHandler):
    def __init__(self, src_dir, dest_dir, data_file):
        self.src_dir = src_dir
        self.dest_dir = dest_dir

        # Initialize data file with an empty list if it doesn't exist or is empty
        if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
            with open(DATA_FILE, 'w') as f:
                json.dump({}, f)
    
    def on_created(self, event):
        if event.is_directory:
            return
        src_path = event.src_path

        # Check if the file still exists at src_path
        if not os.path.exists(src_path):
            print(f"File {src_path} no longer exists.")
            return

        file_name = os.path.basename(src_path)
        dest_path = os.path.join(self.dest_dir, file_name)

        # Pull out preferred classes to filter from filter_preferences
        with open(FILTER_PREFERENCES, 'r') as f:
            CLASSES_TO_FILTER = json.load(f)["Classes"]
            print('Classes to filter, ', CLASSES_TO_FILTER)

        try:
            # After moving the file, classify it
            classification_result = run_classification(src_path)
            if classification_result in CLASSES_TO_FILTER:
                # Duplicate the file before moving it. This duplicates src_path and then lands it in dest_path
                shutil.copy2(src_path, dest_path)
                # shutil.move(src_path, dest_path)
                print(f"File was classified as {classification_result}, preferences are {CLASSES_TO_FILTER}")
                print(f"Moved: {file_name} to {dest_path}")

                # Update data.json file
                self.update_data_file(file_name, classification_result)
            else:
                print(f"File was not classified as per preferences, so it was not duplicated or moved: {file_name}")

            print(f"Classification Result for {file_name}: {classification_result}")
        except Exception as e:
            print(f"Error moving (or classifying) {file_name}: {e}")

    def update_data_file(self, file_name, classification_result):
        try:
            creation_time = datetime.fromtimestamp(os.path.getctime(os.path.join(self.dest_dir, file_name))).strftime('%Y-%m-%d %H:%M:%S')
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                data[file_name] = {"classification_result": classification_result, "creation_time": creation_time}
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print("An error occurred while updating data file:", e)

def start_daemon():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"Fork failed: {e}\n")
        sys.exit(1)
    
    os.chdir("/")
    
    sys.stdout.flush()
    sys.stderr.flush()
    os.close(sys.stdin.fileno())
    os.close(sys.stdout.fileno())
    os.close(sys.stderr.fileno())
    
    sys.stdin = open("/dev/null", "r")
    sys.stdout = open("/dev/null", "a+")
    sys.stderr = open("/dev/null", "a+")
    
    os.umask(0)
    
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

    main()

def stop_and_delete_previous_daemon():
    # Check if lock file exists, indicating a previous daemon
    if os.path.exists(LOCK_FILE):
        # Read the PID of the previous daemon from the lock file
        with open(LOCK_FILE, "r") as f:
            previous_daemon_pid = int(f.read().strip())

        # Check if the previous daemon process is still active
        if is_process_active(previous_daemon_pid):
            # Stop the previous daemon by sending a SIGTERM signal
            os.kill(previous_daemon_pid, signal.SIGTERM)
        
        # Delete the lock file regardless of whether the process is active or not
        os.remove(LOCK_FILE)

def handler(signum, frame):
    sys.exit(0)

def is_process_active(pid):
    return psutil.pid_exists(pid)

def main():
    desktop_dir = os.path.expanduser("~/Desktop")
    copied_file_folder = os.path.join(desktop_dir, "SiloV3/SH")

    # Stop and delete the previous daemon
    stop_and_delete_previous_daemon()

    # Create lock file to indicate the current daemon
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

    if not os.path.exists(copied_file_folder):
        os.mkdir(copied_file_folder)

    event_handler = FileHandler(desktop_dir, copied_file_folder, DATA_FILE)
    observer = Observer()
    observer.schedule(event_handler, path=desktop_dir, recursive=False)
    observer.start()

    try:
        display_process = subprocess.Popen(["python3", os.path.join(os.path.dirname(__file__), "display.py")])

        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--daemonize":
        start_daemon()
    else:
        main()




