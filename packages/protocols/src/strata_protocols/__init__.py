import os
import sys

# Add the current directory to sys.path so the generated modules can find each other
sys.path.insert(0, os.path.dirname(__file__))

from . import agent_service_pb2
from . import agent_service_pb2_grpc

__all__ = ["agent_service_pb2", "agent_service_pb2_grpc"]
