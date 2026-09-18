import subprocess
import time
import sys

def main():
    print("Checking if Ollama is running...")
    import urllib.request
    ollama_process = None
    try:
        urllib.request.urlopen("http://127.0.0.1:11434", timeout=1)
        print("Ollama is already running.")
    except Exception:
        print("Ollama is not running. Starting 'ollama serve' in the background...")
        try:
            ollama_process = subprocess.Popen(
                ["ollama", "serve"], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            time.sleep(2) # Give it a second to boot up
        except FileNotFoundError:
            print("[WARN] Ollama executable not found in PATH! You will need to install or start it manually.")

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
        if ollama_process:
            ollama_process.terminate()
        proc_process.wait()
        gateway_process.wait()

if __name__ == "__main__":
    main()
