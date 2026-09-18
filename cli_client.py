import asyncio
import websockets
import json
import uuid
import sys

async def connect():
    session_id = str(uuid.uuid4())
    uri = f"ws://127.0.0.1:8000/ws/{session_id}"
    print(f"Connecting to {uri}...")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://127.0.0.1:8000/config/models")
            if resp.status_code == 200:
                data = resp.json()
                active = data.get("active", "unknown")
                models = data.get("models", [])
                print(f"--- Model Status ---")
                print(f"Active Model: {active}")
                print(f"Available Models: {', '.join(models) if models else 'None detected'}")
                print(f"--------------------")
                
                if models:
                    choice = input(f"Enter model to use (or press Enter to keep '{active}'): ").strip()
                    if choice and choice in models:
                        resp = await client.post("http://127.0.0.1:8000/config/model", json={"model": choice})
                        if resp.status_code == 200:
                            print(f"[OK] Model switched to {choice}")
                        else:
                            print(f"[ERROR] Failed to switch model")
                    elif choice:
                        print(f"[WARN] Invalid model '{choice}', keeping '{active}'")

    except Exception as e:
        print(f"[Warning] Could not fetch model list: {e}")

    try:
        async with websockets.connect(uri) as websocket:
            print("\nConnected! Type your message (or 'quit' to exit):")
            
            async def receive_messages():
                try:
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        print(f"\n[Agent] {json.dumps(data, indent=2)}")
                except websockets.exceptions.ConnectionClosed:
                    print("\nConnection closed by server.")
                except Exception as e:
                    print(f"\nError receiving message: {e}")

            recv_task = asyncio.create_task(receive_messages())
            
            while True:
                # Use a separate thread or non-blocking way to get input in a real async app
                # For this simple test, this will block the event loop while waiting for input,
                # but it's okay because we're just sending one message at a time.
                user_input = await asyncio.to_thread(input, "> ")
                if user_input.lower() in ['quit', 'exit']:
                    break
                
                payload = {
                    "type": "user_message",
                    "content": user_input
                }
                await websocket.send(json.dumps(payload))
                
            recv_task.cancel()
    except ConnectionRefusedError:
        print("Failed to connect. Is the Gateway service running?")

if __name__ == "__main__":
    try:
        asyncio.run(connect())
    except KeyboardInterrupt:
        print("\nExiting.")
