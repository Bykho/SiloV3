import os
import time
import psutil

# Function to check if the lock file exists
def check_lock_file():
    lock_file = "/tmp/silov2_daemon.lock"
    return os.path.exists(lock_file)

# Function to check if the process is running
def check_process():
    lock_file = "/tmp/silov2_daemon.lock"
    if not os.path.exists(lock_file):
        return False
    with open(lock_file, "r") as f:
        pid = int(f.read().strip())
    return pid in (p.pid for p in psutil.process_iter())

# Test case to check if the code successfully runs as a daemon
def test_daemon():
    # Run the script as a daemon
    os.system("python3 localFileInterceptor.py --daemonize")
    
    # Check if the lock file is created
    assert check_lock_file(), "Lock file not created"
    
    # Check if the process is running
    assert check_process(), "Daemon process not running"
    
    print("Daemon test passed successfully")

if __name__ == "__main__":
    test_daemon()
