from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from strata_core.logging import setup_logging
from .routes import sessions_router, config_router
from .ws.manager import manager
import json

setup_logging()

app = FastAPI(title="Strata API Gateway")

app.include_router(sessions_router, tags=["sessions"])
app.include_router(config_router, tags=["config"])

@app.get("/")
def read_root():
    return {"message": "Strata API Gateway is running"}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "user_message":
                    import asyncio
                    from .rpc.client import agent_client
                    # Run gRPC call in background task so we can keep receiving
                    asyncio.create_task(agent_client.submit_task(session_id, msg.get("content", ""), manager))
                else:
                    await manager.send_json(session_id, {"type": "error", "content": "Unsupported message type"})
            except json.JSONDecodeError:
                await manager.send_json(session_id, {"type": "error", "content": "Invalid JSON"})
    except WebSocketDisconnect:
        manager.disconnect(session_id)

