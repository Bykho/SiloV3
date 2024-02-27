import os
import signal

def stop_daemon():
    lock_file = "/tmp/silov2_daemon.lock"
    if os.path.exists(lock_file):
        with open(lock_file, "r") as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        print("Daemon process terminated successfully.")
        # Remove the lock file
        os.remove(lock_file)
    else:
        print("No daemon process found.")

if __name__ == "__main__":
    stop_daemon()
