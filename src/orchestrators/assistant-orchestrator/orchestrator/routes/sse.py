import json
import asyncio
from contextlib import nullcontext

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader
from fastapi.responses import StreamingResponse
from ska_utils import get_telemetry

from context_directive import parse_context_directives
from jose_types import ExtraData
from model.requests import ConversationMessageRequest
from model.conversation import SseEventType
from collections import namedtuple
from functools import lru_cache
from typing import Any

from .deps import (
    get_agent_catalog,
    get_config,
    get_conn_manager,
    get_conv_manager,
    get_fallback_agent,
    get_rec_chooser,
    get_user_context_cache,
)

conv_manager = get_conv_manager()
conn_manager = get_conn_manager()
rec_chooser = get_rec_chooser()
config = get_config()
agent_catalog = get_agent_catalog()
fallback_agent = get_fallback_agent()
cache_user_context = get_user_context_cache()

router = APIRouter()
header_scheme = APIKeyHeader(name="authorization", auto_error=False)

# Initialize your session_cache and define SessionData tuple structure
SessionData = namedtuple('SessionData', ['conversation', 'request', 'authorization'])
session_cache: dict[str, SessionData] = {}

# Initialize the cache with a TTL (e.g., 5 minutes)
# maxsize determines how many items to keep if TTL doesn't evict them.
# A smaller maxsize coupled with TTL helps manage memory.
#@lru_cache(maxsize=128, ttl=300) # TTL in seconds (5 minutes)
#async def get_and_cache_session_data(user_id: str, conversation_id: str, request: ConversationMessageRequest, authorization: Any):
#    """
#    This function fetches conversation data and caches it.
#    The cache key is implicitly (user_id, conversation_id, request, authorization)
#    This works best if request and authorization are hashable (e.g., simple strings or tuples).
#    """
#    conv = await conv_manager.get_conversation(user_id, conversation_id)
#    return SessionData(conversation=conv, request=request, authorization=authorization)

# Helper function to format SSE messages (still useful if you want event types)
def format_sse_message(data: dict[str, Any], event_type: SseEventType) -> str:
    """Formats data into a Server-Sent Event string with an event type."""
    json_data = json.dumps(data)
    return f"event: {event_type.value}\ndata: {json_data}\n\n"

# Helper function to format only data field for SSE
def format_sse_data_only(data: dict[str, Any]) -> str:
    """Formats data into a Server-Sent Event string with only the data field."""
    json_data = json.dumps(data)
    return f"data: {json_data}\n\n"

@router.post(
    "/conversations/{conversation_id}/messages/sse",
    tags=["Conversations SSE"],
    description="Setup a conversation . Returns new session ID and agent response.",
)
async def add_conversation_sse_message_by_id(
    user_id: str,
    conversation_id: str,
    request: ConversationMessageRequest,
    authorization: str = Depends(header_scheme),
):    
    """
    {0}

    This endpoint initializes a session cache for the specified conversation. 
    After calling this endpoint, you can use the GET endpoint with the conversation ID and user ID 
    to retrieve the conversation data.
    """
    try:
        conv = await conv_manager.get_conversation(user_id, conversation_id)
        session_cache[conversation_id] = SessionData(conversation=conv, request=request, authorization=authorization)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Unable to get conversation with conversation_id: {conversation_id} --- {e}",
        ) from e
    return {"conversation_id": conv.conversation_id, "user_id": conv.user_id}

@router.get(
    "/conversations/{conversation_id}/messages/sse",
    tags=["Conversations SSE"],
    description="Stream back response from agents based on user and session id.",
)
async def stream_conversation_sse_message_by_id(conversation_id: str):
    """
    {0}

    Stream conversation messages using Server-Sent Events (SSE).

    This endpoint allows clients to receive real-time updates for a conversation
    using the previously established session ID. After initializing the session
    via the POST endpoint, clients can use this GET endpoint with EventSource
    or similar SSE-compatible tools to subscribe to the event stream.

    The event stream provides updates such as agent selection, intermediate task
    responses, and the final conversation result.
    """
    jt = get_telemetry()
    
    # --- Initialize Session Data based on conversation_id ---
    try:
        session_data = session_cache.get(conversation_id)
        if not session_data:
            raise HTTPException(
                status_code=404,
                detail=f"Session data not found or expired for conversation_id: {conversation_id}",
            )
        conv = session_data.conversation
        request = session_data.request
        authorization = session_data.authorization
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Unable to find session cache for conversation_id: {conversation_id}",
        ) from e

    async def event_generator():
        in_memory_user_context = None
        if cache_user_context:
            in_memory_user_context = cache_user_context.get_user_context_from_cache(
                user_id=user_id
            ).model_dump()["user_context"]
            await conv_manager.add_transient_context(conv, in_memory_user_context)

        with (
            jt.tracer.start_as_current_span("conversation-turn")
            if jt.telemetry_enabled()
            else nullcontext()
        ):
            # --- Call Agent Selector Agent ---
            with (
                jt.tracer.start_as_current_span("choose-recipient")
                if jt.telemetry_enabled()
                else nullcontext()
            ):
                try:
                    selected_agent = await rec_chooser.choose_recipient(request.message, conv)
                except Exception as e:
                    yield format_sse_message(
                        {"error": f"Error retrieving agent: {e}"},
                        SseEventType.UNKNOWN
                    )
                    return 

                # Determine the selected agent
                if selected_agent.agent_name not in agent_catalog.agents:
                    agent = fallback_agent
                    sel_agent_name = fallback_agent.name
                else:
                    agent = agent_catalog.agents[selected_agent.agent_name]
                    sel_agent_name = agent.name

            # --- Orchestrator Response: Agent Chosen ---
            # Send agent chosen event
            yield format_sse_message(
                {"task": "agent_chosen", "agent_name": sel_agent_name},
                SseEventType.ORCH_INTERMEDIATE_TASK_RESPONSE
            )

            # --- Update History User ---
            # Add user message to conversation history
            with (
                jt.tracer.start_as_current_span("update-history-user")
                if jt.telemetry_enabled()
                else nullcontext()
            ):
                try:
                    await conv_manager.add_user_message(conv, request.message, sel_agent_name)
                    # Send intermediate event for user message added to history
                    yield format_sse_message(
                        {"task": "user_message_added", "message": "User message added to history."},
                        SseEventType.ORCH_INTERMEDIATE_TASK_RESPONSE
                    )
                except Exception as e:
                    # Format error event using helper function
                    yield format_sse_message(
                        {"error": f"Error adding user message to history: {e}"},
                        SseEventType.UNKNOWN
                    )
                    return

            # --- Agent Response (Streaming Partial) and (Final Response) ---
            with (
                jt.tracer.start_as_current_span("agent-streaming-partial-response")
                if jt.telemetry_enabled()
                else nullcontext()
            ):
                try:
                    # Initialize agent_response to be an empty string, will be populated from final output
                    agent_response = ""
                    async for raw_sse_line in agent.invoke_sse(conv, authorization):
                        if raw_sse_line:
                            yield f"{raw_sse_line}"
                    # Parse and retrieve final response output for adding to conversation history
                    line_for_parsing = raw_sse_line.strip()
                    if line_for_parsing.startswith("event: final-response"):
                        # Extract the data part from the line
                        data_start_index = line_for_parsing.find("data: ")
                        if data_start_index != -1:
                            event_data_str = line_for_parsing[data_start_index + len("data: "):].strip()
                            try:
                                parsed_data = json.loads(event_data_str)
                                if "output_raw" in parsed_data:
                                    agent_response = parsed_data["output_raw"]
                            except json.JSONDecodeError:
                                print(f"Warning: Could not parse final-response data as JSON: {event_data_str}")
                        else:
                            print(f"Warning: 'final-response' event missing 'data:' part: {line_for_parsing}")
                    await asyncio.sleep(0.001)

                except Exception as e:
                    print(f"Error during agent streaming: {e}")
                    yield f"event: {SseEventType.UNKNOWN}\ndata: {json.dumps({'error': f'Error during agent streaming: {e}'})}\n\n"

            # --- Update History Assistant ---
            with (
                jt.tracer.start_as_current_span("update-history-assistant")
                if jt.telemetry_enabled()
                else nullcontext()
            ):
                try:
                    await conv_manager.add_agent_message(conv, agent_response, sel_agent_name)
                    # Send intermediate event for assistant message added to history
                    yield format_sse_message(
                        {"task": "agent_message_added", "message": "Agent response added to history."},
                        SseEventType.ORCH_INTERMEDIATE_TASK_RESPONSE
                    )
                except Exception as e:
                    yield format_sse_message(
                        {"error": f"Error adding assistant response to history: {e}"},
                        SseEventType.UNKNOWN
                    )
                    return # Critical error, stop streaming

    # Return StreamingResponse with the event_generator and correct media type
    return StreamingResponse(event_generator(), media_type="text/event-stream")
