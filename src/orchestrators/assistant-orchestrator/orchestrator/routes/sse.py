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
from model.conversation import SseEventType, SseMessage, SseFinalMessage, SseError
from collections import namedtuple
from functools import lru_cache
from typing import Any
from agents import Conversation

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

# Helper function to format SSE messages
def format_sse_message(data: dict[str, Any], event_type: SseEventType) -> str:
    """Formats data into a Server-Sent Event string with an event type."""
    json_data = json.dumps(data)
    return f"event: {event_type.value}\ndata: {json_data}\n\n"

# Main function to Add and Stream Conversation Message through SSE
async def sse_event_response(
    conv: Conversation,
    request: ConversationMessageRequest,
    authorization: Any,
):
    jt = get_telemetry()
    in_memory_user_context = None
    if cache_user_context:
        in_memory_user_context = cache_user_context.get_user_context_from_cache(
            user_id=conv.user_id
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
                sse_error = SseError(
                    error=f"Error retrieving agent: {e}",
                )
                yield format_sse_message(
                    sse_error.model_dump(),
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
        sse_agent = SseMessage(
            task="agent_chosen",
            message=f"{sel_agent_name} was selected by agent chooser."
        )
        yield format_sse_message(
            sse_agent.model_dump(),
            SseEventType.INTERMEDIATE_TASK_RESPONSE
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
                sse_message = SseMessage(
                    task="user_message_added",
                    message="User message added to history."
                )
                yield format_sse_message(
                    sse_message.model_dump(),
                    SseEventType.INTERMEDIATE_TASK_RESPONSE
                )
            except Exception as e:
                sse_error = SseError(
                    error=f"Error adding user message to history: {e}",
                )
                yield format_sse_message(
                    sse_error.model_dump(),
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
                # Initialize agent_response to be an empty string, will be populated from final raw output
                agent_response = ""
                async for content in agent.invoke_sse(conv, authorization):
                    try:
                        # Check if extra data and process extra data, as done in ws
                        extra_data: ExtraData = ExtraData.new_from_json(content)
                        context_directives = parse_context_directives(extra_data)
                        await conv_manager.process_context_directives(conv, context_directives)
                    except Exception as e:
                        print(e)
                        # Yield the agent response stream directly
                        if content:
                            yield f"{content}"
                        # Check for final response, and if so parse the output raw data
                        if content.startswith("event:"):
                            last_event_type = content[len("event:"):].strip()
                        elif content.startswith("data:"):
                            if last_event_type == "final-response":
                                json_data_str = content[len("data: "):].strip()
                                try:
                                    data = json.loads(json_data_str)
                                    agent_response = data.get("output_raw", "")
                                except json.JSONDecodeError:
                                    print(f"Error decoding JSON: {json_data_str}")
                        await asyncio.sleep(0.001)
            except Exception as e:
                sse_error = SseError(
                    error=f"Error during agent streaming: {e}",
                )
                yield format_sse_message(
                    sse_error.model_dump(),
                    SseEventType.UNKNOWN
                )
                return

        # --- Update History Agent ---
        with (
            jt.tracer.start_as_current_span("update-history-assistant")
            if jt.telemetry_enabled()
            else nullcontext()
        ):
            try:
                # Send intermediate event for agent message added to history
                await conv_manager.add_agent_message(conv, agent_response, sel_agent_name)
                sse_message = SseMessage(
                    task="agent_message_added",
                    message="Agent response added to history"
                )
                yield format_sse_message(
                    sse_message.model_dump(),
                    SseEventType.INTERMEDIATE_TASK_RESPONSE
                )
            except Exception as e:
                sse_error = SseError(
                    error=f"Error adding agent response to history:{e}",
                )
                yield format_sse_message(
                    sse_error.model_dump(),
                    SseEventType.UNKNOWN
                )
                return
            
        # --- Orchestrator Final Response ---
        with (
            jt.tracer.start_as_current_span("update-history-assistant")
            if jt.telemetry_enabled()
            else nullcontext()
        ):
            try:
                # Send the final response from the orchestrator
                conversation_result = await conv_manager.get_last_response(conv)
                final_response = SseFinalMessage(
                    task="orchestrator_final_response",
                    conversation=conversation_result
                )
                yield format_sse_message(
                    final_response.model_dump(),
                    SseEventType.FINAL_RESPONSE
                )
            except Exception as e:
                sse_error = SseError(
                    error=f"Orchestrator failed to finalize conversation: {e}",
                )
                yield format_sse_message(
                    sse_error.model_dump(),
                    SseEventType.UNKNOWN
                )

@router.post(
    "/conversations/{conversation_id}/sse",
    tags=["Conversations SSE"],
    description="Stream back response from agents based on user and session id.",
)
async def add_and_stream_conversation_sse_message_by_id(
    user_id: str,
    conversation_id: str,
    request: ConversationMessageRequest,
    authorization: str = Depends(header_scheme),
):    
    """
    {0}

    This endpoint initializes a session cache for the specified conversation and streams back 
    the response from agents based on user and conversation id.
    """
    try:
        conv = await conv_manager.get_conversation(user_id, conversation_id)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Unable to get conversation with conversation_id: {conversation_id} --- {e}",
        ) from e
    
    # Return StreamingResponse with the event_generator and correct media type
    return StreamingResponse(sse_event_response(conv, request, authorization), media_type="text/event-stream")


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
    description="Stream back response from agents based on user and conversation id.",
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
        del session_cache[conversation_id]
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Unable to find session cache for conversation_id: {conversation_id}",
        ) from e

    # Return StreamingResponse with the event_generator and correct media type
    return StreamingResponse(sse_event_response(conv, request, authorization), media_type="text/event-stream")
