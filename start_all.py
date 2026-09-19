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
        print("Ollama is not running. Attempting to start 'ollama serve'...")
        try:
            ollama_process = subprocess.Popen(
                ["ollama", "serve"], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            time.sleep(2)
        except FileNotFoundError:
            print("[WARN] Ollama is not installed on this system!")
            choice = input("Would you like Strata to automatically download and install Ollama for you? (y/n): ").strip().lower()
            if choice == 'y':
                import os
                print("Downloading OllamaSetup.exe...")
                installer_path = os.path.join(os.environ.get("TEMP", "C:\\temp"), "OllamaSetup.exe")
                urllib.request.urlretrieve("https://ollama.com/download/OllamaSetup.exe", installer_path)
                print("Running installer... (Please accept any Administrator prompts)")
                # Run the installer and wait for it to finish
                subprocess.run([installer_path], check=True)
                print("Ollama installed successfully! Please restart this terminal for PATH changes to take effect, or restart start_all.py.")
                sys.exit(0)
            else:
                print("Please install Ollama manually from https://ollama.com/ to use local models.")

    print("Starting Processing Service...")
    proc_process = subprocess.Popen([sys.executable, "start_processing.py"])
    
    print("Starting Gateway Service...")
    gateway_process = subprocess.Popen([sys.executable, "start_gateway.py"])
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        import os
        if os.name == 'nt':
            # Force kill process tree on Windows to prevent zombies
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc_process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(gateway_process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if ollama_process:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(ollama_process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            proc_process.terminate()
            gateway_process.terminate()
            if ollama_process:
                ollama_process.terminate()
            proc_process.wait()
            gateway_process.wait()

if __name__ == "__main__":
    main()
