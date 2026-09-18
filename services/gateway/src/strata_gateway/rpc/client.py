import grpc
import asyncio
import json
from loguru import logger
from strata_protocols import agent_service_pb2, agent_service_pb2_grpc
from strata_core.config import settings

class AgentClient:
    def __init__(self):
        self.channel = grpc.aio.insecure_channel(f"{settings.gateway_host}:{settings.grpc_port}")
        self.stub = agent_service_pb2_grpc.AgentServiceStub(self.channel)
        
    async def submit_task(self, session_id: str, task: str, ws_manager):
        try:
            request = agent_service_pb2.TaskRequest(session_id=session_id, task=task)
            async for event in self.stub.SubmitTask(request):
                # Forward gRPC event back to WebSocket client
                payload = {
                    "type": event.type,
                    "content": event.content,
                }
                if event.tool:
                    payload["tool"] = event.tool
                if event.args_json:
                    try:
                        payload["args"] = json.loads(event.args_json)
                    except:
                        payload["args"] = event.args_json
                
                await ws_manager.send_json(session_id, payload)
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e}")
            await ws_manager.send_json(session_id, {"type": "error", "content": str(e)})

agent_client = AgentClient()
