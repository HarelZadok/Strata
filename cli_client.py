import asyncio
import websockets
import json
import uuid
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding='utf-8')

async def connect():
    import getpass
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", help="Profile ID to use for the session", default=None)
    args, unknown = parser.parse_known_args()
    
    # Use the provided profile ID, or fallback to OS username as persistent profile ID
    profile_id = args.profile.lower().replace(" ", "_") if args.profile else getpass.getuser().lower().replace(" ", "_")
    uri = f"ws://127.0.0.1:8000/ws/{profile_id}"
    print(f"Connecting to {uri} as profile '{profile_id}'...")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://127.0.0.1:8000/config/models")
            if resp.status_code == 200:
                data = resp.json()
                active = data.get("active", "unknown")
                models = data.get("models") # Now returns None if Ollama is unreachable
                print(f"--- Strata Backend Status ---")
                print(f"Active Configured Model: {active}")
                if models is None:
                    print("\n[CRITICAL] Ollama is NOT running or not installed!")
                    print("Strata uses Ollama to run 100% free, local AI models.")
                    print("\nTo fix this:")
                    print("  1. Download and install Ollama from: https://ollama.com/")
                    print("  2. Open a new terminal and download a model, for example:")
                    print("       - ollama pull qwen2.5:7b       (Fast generalist)")
                    print("       - ollama pull gpt-oss:20b      (OpenAI reasoning)")
                    print("       - ollama pull llama3.1         (Meta's flagship)")
                    print("       - ollama pull deepseek-coder-v2(Coding specialist)")
                    print("  3. Restart this CLI.\n")
                    print("-----------------------------")
                    return # Exit the client so they can fix it
                else:
                    print(f"Available Local Models: {', '.join(models) if models else 'No models downloaded yet!'}")
                    if not models:
                        print("  -> Type '/model add' in the chat to download your first model!")
                    print(f"-----------------------------")
                    print("\nTip: Type '/model' in the chat to manage or install AI models.")
                    
    except Exception as e:
        print(f"[Warning] Could not fetch model list: {e}")

    try:
        async with websockets.connect(uri) as websocket:
            print("\nConnected! Type your message (or 'quit' to exit):")
            
            agent_done = asyncio.Event()
            agent_done.set()
            
            async def receive_messages():
                try:
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if data.get("type") == "agent_token":
                            print(data.get("content", ""), end="", flush=True)
                        elif data.get("type") == "task_complete":
                            print() # Just newline
                            agent_done.set()
                        elif data.get("type") == "agent_action":
                            tool = data.get("tool")
                            args = data.get("args", {})
                            print(f"\n[⚡ Agent Action: {tool}({args})]\n[Agent] ", end="", flush=True)
                        elif data.get("type") == "error":
                            print(f"\n[ERROR] {data.get('content')}")
                            agent_done.set()
                        else:
                            # For anything else
                            pass
                except websockets.exceptions.ConnectionClosed:
                    print("\nConnection closed by server.")
                    agent_done.set()
                except Exception as e:
                    print(f"\nError receiving message: {e}")
                    agent_done.set()

            recv_task = asyncio.create_task(receive_messages())
            
            while True:
                await agent_done.wait()
                user_input = await asyncio.to_thread(input, "> ")
                user_input = user_input.strip()
                if not user_input:
                    continue
                if user_input.lower() in ['quit', 'exit']:
                    break
                    
                if user_input.startswith("/model"):
                    import httpx
                    import subprocess
                    parts = user_input.split()
                    
                    if len(parts) == 1: # Just `/model`
                        async with httpx.AsyncClient() as c:
                            resp = await c.get("http://127.0.0.1:8000/config/models")
                            data = resp.json()
                            models = data.get("models", [])
                            print(f"\n--- Installed Models ---")
                            print(f"Active: {data.get('active')}")
                            print(f"Available: {', '.join(models)}")
                            choice = await asyncio.to_thread(input, "Enter model to switch to (or press Enter to cancel): ")
                            if choice.strip() in models:
                                await c.post("http://127.0.0.1:8000/config/model", json={"model": choice.strip()})
                                print(f"[OK] Switched to {choice.strip()}")
                            elif choice.strip():
                                print(f"[ERROR] '{choice.strip()}' is not installed. Use '/model add' to install it.")
                    
                    elif parts[1] == "list":
                        async with httpx.AsyncClient() as c:
                            resp = await c.get("http://127.0.0.1:8000/config/models")
                            installed = resp.json().get("models", [])
                        print("\n--- Model Library ---")
                        print(f"Installed: {', '.join(installed) if installed else 'None'}")
                        print("\nRecommended Models to Download:")
                        print("  - qwen2.5:7b       (Fast generalist, Default)")
                        print("  - gpt-oss:20b      (OpenAI's reasoning model, 16GB RAM)")
                        print("  - llama3.1         (Meta's flagship 8B)")
                        print("  - deepseek-coder-v2(Elite coding model)")
                        print("\nTip: Type '/model add' to install one of these!")
                        
                    elif parts[1] == "add":
                        model_to_add = parts[2] if len(parts) > 2 else await asyncio.to_thread(input, "Enter model name to install (e.g. qwen2.5:7b): ")
                        model_to_add = model_to_add.strip()
                        if model_to_add:
                            print(f"\n[Strata] Asking Ollama to download '{model_to_add}'...")
                            print("[Strata] This may take a few minutes depending on your internet connection.\n")
                            # Run ollama pull and stream output to console
                            try:
                                await asyncio.to_thread(subprocess.run, ["ollama", "pull", model_to_add], check=True)
                                print(f"\n[OK] Successfully installed {model_to_add}!")
                                print(f"Type '/model' to switch to it.")
                            except Exception as e:
                                print(f"\n[ERROR] Failed to download model: {e}")
                    else:
                        print(f"Unknown command. Try: /model, /model list, /model add")
                    continue
                
                payload = {
                    "type": "user_message",
                    "content": user_input
                }
                print("[Agent] ", end="", flush=True)
                agent_done.clear()
                await websocket.send(json.dumps(payload))
                
            recv_task.cancel()
    except ConnectionRefusedError:
        print("Failed to connect. Is the Gateway service running?")

if __name__ == "__main__":
    try:
        asyncio.run(connect())
    except KeyboardInterrupt:
        print("\nExiting.")
