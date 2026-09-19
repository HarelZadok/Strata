from langgraph.graph import StateGraph, END
from strata_processing.state import AgentState
from strata_processing.tools import registered_tools
from strata_core.llm_provider import LLMClient
from langchain_core.messages import AIMessage, ToolMessage, ToolCall
import json
from loguru import logger

llm = LLMClient()

def convert_tools_to_openai_schema(tools):
    schemas = []
    for t in tools:
        schema = {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.args_schema.schema() if t.args_schema else {"type": "object", "properties": {}}
            }
        }
        schemas.append(schema)
    return schemas

tool_schemas = convert_tools_to_openai_schema(registered_tools)
tools_by_name = {t.name: t for t in registered_tools}

from langchain_core.runnables.config import RunnableConfig

async def llm_reasoning(state: AgentState, config: RunnableConfig):
    """Invokes the LLM to decide the next action."""
    messages = state["messages"]
    callbacks = config.get("configurable", {})
    on_token = callbacks.get("on_token")
    
    # Convert Langchain messages to dicts for our LLMClient
    formatted_messages = []
    for msg in messages:
        if msg.type == "human":
            formatted_messages.append({"role": "user", "content": msg.content})
        elif msg.type == "ai":
            d = {"role": "assistant", "content": msg.content or ""}
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                # Convert LangChain ToolCall to OpenAI format
                d["tool_calls"] = []
                for idx, tc in enumerate(msg.tool_calls):
                    d["tool_calls"].append({
                        "id": tc.get("id") or f"call_{idx}",
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["args"])
                        }
                    })
            formatted_messages.append(d)
        elif msg.type == "system":
            formatted_messages.append({"role": "system", "content": msg.content})
        elif msg.type == "tool":
            formatted_messages.append({
                "role": "tool",
                "tool_call_id": msg.tool_call_id,
                "content": str(msg.content)
            })

    full_response = ""
    tool_calls_made = []
    
    async for chunk in llm.chat_stream(formatted_messages, tools=tool_schemas):
        if chunk["type"] == "content":
            full_response += chunk["data"]
            if on_token:
                await on_token(chunk["data"])
        elif chunk["type"] == "tool_call":
            tool_calls_made.append(chunk["data"])

            
    parsed_tool_calls = []
    for tc in tool_calls_made:
        try:
            args = json.loads(tc["function"]["arguments"]) if tc["function"]["arguments"] else {}
        except Exception:
            args = {}
        parsed_tool_calls.append(ToolCall(
            name=tc["function"]["name"],
            args=args,
            id=tc.get("id", f"call_{len(parsed_tool_calls)}")
        ))

    # Return the new AIMessage
    return {"messages": [AIMessage(content=full_response, tool_calls=parsed_tool_calls)]}

async def tool_execution(state: AgentState, config: RunnableConfig):
    """Executes tools requested by the LLM."""
    last_message = state["messages"][-1]
    tool_messages = []
    
    callbacks = config.get("configurable", {})
    on_tool = callbacks.get("on_tool")
    safety_mode = callbacks.get("safety_mode", "auto")
    
    # Check if the user's last message contains approval
    last_human_msg = next((msg.content.lower() for msg in reversed(state["messages"]) if msg.type == "human"), "")
    is_approved = "approve" in last_human_msg or "yes" in last_human_msg
    
    for tool_call in last_message.tool_calls:
        fn_name = tool_call["name"]
        args = tool_call["args"]
        call_id = tool_call["id"]
        
        # Risk Evaluation
        is_dangerous = fn_name in ["click_element", "type_text"]
        
        if is_dangerous:
            if safety_mode == "hitl" and not is_approved:
                logger.warning(f"HITL blocked {fn_name}. Awaiting user approval.")
                result = f"ACTION BLOCKED (Safety Mode: HITL). You must ask the user to explicitly say 'approve' before you can execute {fn_name}."
                tool_messages.append(ToolMessage(content=result, tool_call_id=call_id))
                continue
                
            if safety_mode == "smart":
                # Smart mode: only block high-risk actions (typing). Clicks are considered medium-risk and auto-pass.
                is_high_risk = fn_name in ["type_text"]
                if is_high_risk and not is_approved:
                    logger.warning(f"Smart safety blocked {fn_name}. Awaiting user approval.")
                    result = f"ACTION BLOCKED (Safety Mode: SMART). The {fn_name} tool is high-risk. Ask the user to say 'approve' before executing."
                    tool_messages.append(ToolMessage(content=result, tool_call_id=call_id))
                    continue
        
        logger.info(f"Executing tool: {fn_name} with args: {args}")
        if on_tool:
            await on_tool(fn_name, args)
        
        if fn_name in tools_by_name:
            tool_instance = tools_by_name[fn_name]
            try:
                # Some tools might need session_id injected if they require it
                if "session_id" in tool_instance.args_schema.__fields__:
                    args["session_id"] = state["session_id"]
                result = await tool_instance.ainvoke(args)
            except Exception as e:
                result = f"Error executing tool {fn_name}: {e}"
        else:
            result = f"Unknown tool: {fn_name}"
            
        tool_messages.append(ToolMessage(content=str(result), tool_call_id=call_id))
        
    return {"messages": tool_messages}

def should_continue(state: AgentState):
    """Determines if we need to execute tools or if the turn is finished."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_execution"
    return END

# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("llm_reasoning", llm_reasoning)
workflow.add_node("tool_execution", tool_execution)

workflow.set_entry_point("llm_reasoning")
workflow.add_conditional_edges("llm_reasoning", should_continue, {
    "tool_execution": "tool_execution",
    END: END
})
workflow.add_edge("tool_execution", "llm_reasoning")

app = workflow.compile()
