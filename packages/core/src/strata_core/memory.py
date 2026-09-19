import json
import os
from pathlib import Path
from typing import Dict, Any
from loguru import logger

def get_memory_path(session_id: str = "default") -> str:
    os.makedirs(".local", exist_ok=True)
    return f".local/memory_{session_id}.json"

def load_memory(session_id: str = "default") -> Dict[str, Any]:
    """Loads the permanent memory database from the local filesystem."""
    memory_path = get_memory_path(session_id)
    if os.path.exists(memory_path):
        try:
            with open(memory_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {"facts": []}

def save_memory(memory_data: Dict[str, Any], session_id: str = "default"):
    """Saves the permanent memory database to the local filesystem."""
    memory_path = get_memory_path(session_id)
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(memory_data, f, indent=2)

def manage_memory(action: str, fact: str, old_fact: str = None, session_id: str = "default") -> str:
    """Add, update, or delete an important fact about the user in permanent memory."""
    from loguru import logger
    
    memory_data = load_memory(session_id)
    facts = memory_data.get("facts", [])
    
    if action == "add":
        if fact not in facts:
            facts.append(fact)
            logger.info(f"Memory added [{session_id}]: {fact}")
            result = f"Successfully added fact: {fact}"
        else:
            result = f"Fact already exists in memory: {fact}"
            
    elif action == "update":
        if old_fact and old_fact in facts:
            idx = facts.index(old_fact)
            facts[idx] = fact
            logger.info(f"Memory updated [{session_id}]: {old_fact} -> {fact}")
            result = f"Successfully updated fact from '{old_fact}' to '{fact}'"
        else:
            if fact not in facts:
                facts.append(fact)
                logger.info(f"Memory added (update fallback) [{session_id}]: {fact}")
                result = f"Could not find exact old fact '{old_fact}', but added new fact: {fact}"
            else:
                result = f"Could not find exact old fact '{old_fact}', and new fact already exists: {fact}"
            
    elif action == "delete":
        if fact in facts:
            facts.remove(fact)
            logger.info(f"Memory deleted [{session_id}]: {fact}")
            result = f"Successfully deleted fact: {fact}"
        else:
            result = f"Fact not found in memory, could not delete: {fact}"
            
    else:
        result = f"Unknown action: {action}"
        
    memory_data["facts"] = facts
    save_memory(memory_data, session_id)
    return result

def get_user_profile(session_id: str = "default") -> str:
    """Returns a formatted string of all stored facts about the user, for use as a tool result."""
    mem = load_memory(session_id)
    facts = mem.get("facts", [])
    if not facts:
        return "No information about this user has been stored yet."
    return "Here is what I know about the user:\n" + "\n".join([f"- {f}" for f in facts])

def get_system_prompt_with_memory(session_id: str = "default") -> str:
    """Returns a clean system prompt. Facts are NOT injected here — the model retrieves them via tool call."""
    return (
        "You are Strata, a highly capable and natural AI companion. "
        "Talk like a real person — warm, casual, direct. Never use robotic phrases like 'as an AI' or 'according to my data'.\n\n"
        "You have a tool called `get_user_profile` that retrieves stored facts about the user. "
        "You MUST call it when the user asks a question about themselves (e.g. 'What is my name?', 'What do you know about me?', 'Who am I?'). "
        "Also call it when you genuinely need personal context to give a helpful answer (e.g. for a personalized recommendation). "
        "Do NOT call it for greetings, general questions, or small talk. "
        "If you don't know something about the user after calling the tool, just say so naturally and ask them."
    )
