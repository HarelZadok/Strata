import subprocess
import time
import sys

def main():
    print("Starting Processing Service...")
    proc_process = subprocess.Popen([sys.executable, "start_processing.py"])
    
    print("Starting Gateway Service...")
    gateway_process = subprocess.Popen([sys.executable, "start_gateway.py"])
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        proc_process.terminate()
        gateway_process.terminate()
        proc_process.wait()
        gateway_process.wait()

if __name__ == "__main__":
    main()
