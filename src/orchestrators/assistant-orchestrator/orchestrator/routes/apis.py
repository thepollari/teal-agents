from .deps import (
    get_conv_manager,
    get_conn_manager,
    get_rec_chooser,
    get_config,
    get_agent_catalog,
    get_fallback_agent,
)
from contextlib import nullcontext
from fastapi import FastAPI, APIRouter
from connection_manager import ConnectionManager

conv_manager = get_conv_manager()
conn_manager = get_conn_manager()
rec_chooser = get_rec_chooser()
config = get_config()
agent_catalog = get_agent_catalog()
fallback_agent = get_fallback_agent()

router = APIRouter()

@router.get("/conversations/{session_id}", tags=["Conversations"],
         description="Get the full conversation history based on a session id.")
async def get_conversation_by_id(user_id: str, session_id: str):
    conv = conv_manager.get_conversation(user_id, session_id)
    return {"conversation": conv}

@router.post("/conversation/new_conversation", tags=["Conversations"],
         description="Start a new conversation. Returns new session ID and agent response.")
async def add_conversation(user_id: str, is_resumed: bool):
    conv = conv_manager.new_conversation(user_id, is_resumed)
    return {"conversation": conv}

@router.get("/healthcheck", tags=["Health"],
         description="Check the health status of the application.")
async def healthcheck():
    return {"status": "healthy"}
