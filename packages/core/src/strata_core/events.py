from pydantic import BaseModel, Field
from typing import Literal, Any

class BaseEvent(BaseModel):
    type: str

class UserMessageEvent(BaseEvent):
    type: Literal["user_message"] = "user_message"
    content: str

class AgentTokenEvent(BaseEvent):
    type: Literal["agent_token"] = "agent_token"
    content: str

class AgentActionEvent(BaseEvent):
    type: Literal["agent_action"] = "agent_action"
    tool: str
    args: dict[str, Any]

class HITLRequestEvent(BaseEvent):
    type: Literal["hitl_request"] = "hitl_request"
    action: str
    path: str | None = None
    args: dict[str, Any] | None = None

class HITLResponseEvent(BaseEvent):
    type: Literal["hitl_response"] = "hitl_response"
    approved: bool

class TaskCompleteEvent(BaseEvent):
    type: Literal["task_complete"] = "task_complete"
    summary: str
