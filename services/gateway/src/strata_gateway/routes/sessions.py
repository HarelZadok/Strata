from fastapi import APIRouter
import uuid

router = APIRouter()

@router.post("/sessions")
def create_session():
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}

@router.get("/sessions/{session_id}/history")
def get_session_history(session_id: str):
    return {"history": []}
