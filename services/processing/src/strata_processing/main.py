import grpc
from concurrent import futures
import json
import asyncio
from strata_protocols import agent_service_pb2
from strata_protocols import agent_service_pb2_grpc
from strata_core.logging import setup_logging
from strata_core.config import settings

setup_logging()
from loguru import logger

class AgentService(agent_service_pb2_grpc.AgentServiceServicer):
    async def SubmitTask(self, request, context):
        logger.info(f"Received task for session {request.session_id}: {request.task}")
        from strata_core.llm_provider import LLMClient
        llm = LLMClient()
        
        # Stream the LLM response back as agent_token events
        messages = [{"role": "user", "content": request.task}]
        try:
            async for chunk in llm.chat_stream(messages):
                yield agent_service_pb2.TaskEvent(
                    type="agent_token",
                    content=chunk
                )
            yield agent_service_pb2.TaskEvent(
                type="task_complete",
                content="LLM generation finished."
            )
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            yield agent_service_pb2.TaskEvent(
                type="error",
                content=str(e)
            )


async def serve():
    server = grpc.aio.server()
    agent_service_pb2_grpc.add_AgentServiceServicer_to_server(AgentService(), server)
    address = f"[::]:{settings.grpc_port}"
    server.add_insecure_port(address)
    logger.info(f"Processing Service starting on {address}")
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())
