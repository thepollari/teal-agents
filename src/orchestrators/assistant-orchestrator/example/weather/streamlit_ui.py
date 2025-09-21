from typing import Any

import requests
import streamlit as st


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_url" not in st.session_state:
        st.session_state.agent_url = "http://localhost:8000"
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = "streamlit_user"


def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def create_conversation(user_id: str) -> dict[str, Any]:
    try:
        response = requests.post(
            f"{st.session_state.agent_url}/DemoAgentOrchestrator/0.1/conversations",
            params={"user_id": user_id},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Failed to create conversation: {response.status_code} - {response.text}"
            }
    except Exception as e:
        return {
            "error": f"Failed to create conversation: {str(e)}"
        }


def call_weather_agent(user_input: str, chat_history: list) -> dict[str, Any]:
    try:
        if not st.session_state.conversation_id:
            conv_result = create_conversation(st.session_state.user_id)
            if "error" in conv_result:
                return conv_result
            st.session_state.conversation_id = conv_result["conversation_id"]

        payload = {"message": user_input}
        
        response = requests.post(
            f"{st.session_state.agent_url}/DemoAgentOrchestrator/0.1/conversations/{st.session_state.conversation_id}/messages",
            params={"user_id": st.session_state.user_id},
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer dummy_token"
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            conversation = result.get("conversation", [])
            if conversation:
                for msg in reversed(conversation):
                    if "sender" in msg:
                        return {"output_raw": msg["content"]}
                return {"output_raw": "No agent response found"}
            else:
                return {"output_raw": "Empty conversation"}
        else:
            return {
                "error": f"Agent request failed with status {response.status_code}: {response.text}"
            }

    except requests.exceptions.ConnectionError:
        return {
            "error": "Could not connect to assistant orchestrator. Make sure it's running on http://localhost:8000"
        }
    except requests.exceptions.Timeout:
        return {
            "error": "Request to assistant orchestrator timed out. Please try again."
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}"
        }


def format_weather_response(response_text: str) -> str:
    try:
        if "temperature" in response_text.lower() and "°f" in response_text.lower():
            lines = response_text.split('\n')
            formatted_lines = []

            for line in lines:
                keywords = ["temperature", "humidity", "wind", "weather"]
                if any(keyword in line.lower() for keyword in keywords):
                    formatted_lines.append(f"🌡️ {line}")
                elif "city" in line.lower() or "location" in line.lower():
                    formatted_lines.append(f"📍 {line}")
                else:
                    formatted_lines.append(line)

            return '\n'.join(formatted_lines)
    except Exception:
        pass

    return response_text


def main():
    st.set_page_config(
        page_title="Weather Agent Chat",
        page_icon="🌤️",
        layout="wide"
    )

    initialize_session_state()

    st.title("🌤️ Weather Agent Chat (Assistant Orchestrator)")
    st.markdown("Ask me about the weather in any city around the world! Powered by Assistant Orchestrator.")

    with st.sidebar:
        st.header("⚙️ Configuration")

        agent_url = st.text_input(
            "Assistant Orchestrator URL",
            value=st.session_state.agent_url,
            help="URL where the assistant orchestrator is running"
        )
        st.session_state.agent_url = agent_url

        st.header("📋 Status")

        try:
            health_response = requests.get(f"{agent_url}/DemoAgentOrchestrator/0.1/healthcheck", timeout=5)
            if health_response.status_code == 200:
                st.success("✅ Assistant Orchestrator is running")
            else:
                st.error("❌ Assistant Orchestrator health check failed")
        except Exception:
            st.error("❌ Cannot connect to Assistant Orchestrator")

        st.header("💡 Example Queries")
        st.markdown("""
        - "What's the weather in New York?"
        - "How's the weather in Tokyo today?"
        - "Tell me about the weather in London"
        - "What are the coordinates of Paris?"
        - "Is it raining in Seattle?"
        """)

        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.rerun()

        if st.button("🔄 New Conversation"):
            st.session_state.conversation_id = None
            st.rerun()

    display_chat_history()

    if prompt := st.chat_input("Ask about weather in any city..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Getting weather information..."):
                chat_history = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages[:-1]
                ]
                chat_history.append({"role": "user", "content": prompt})

                response = call_weather_agent(prompt, chat_history)

                if "error" in response:
                    error_message = f"❌ **Error:** {response['error']}"
                    st.markdown(error_message)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message
                    })
                else:
                    try:
                        if "output_raw" in response:
                            agent_response = response["output_raw"]
                        elif "output_pydantic" in response and response["output_pydantic"]:
                            agent_response = str(response["output_pydantic"])
                        else:
                            agent_response = (
                                "I received your request but couldn't generate a proper response."
                            )

                        formatted_response = format_weather_response(agent_response)
                        st.markdown(formatted_response)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": formatted_response
                        })

                        if "token_usage" in response:
                            token_info = response["token_usage"]
                            st.caption(f"🔢 Tokens used: {token_info.get('total_tokens', 'N/A')}")

                    except Exception as e:
                        error_message = f"❌ **Error processing response:** {str(e)}"
                        st.markdown(error_message)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_message
                        })


if __name__ == "__main__":
    main()
