from typing import Any

import requests
import streamlit as st

from assets import (
    CLEAR_ICON,
    ERROR_ICON,
    EXAMPLES_ICON,
    LOCATION_ICON,
    SETTINGS_ICON,
    STATUS_ICON,
    SUCCESS_ICON,
    TEMPERATURE_ICON,
    TOKENS_ICON,
    WEATHER_ICON,
)


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_url" not in st.session_state:
        st.session_state.agent_url = "http://localhost:8000"
    if "ta_agw_key" not in st.session_state:
        st.session_state.ta_agw_key = "dummy_key"


def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def call_weather_agent(user_input: str, chat_history: list) -> dict[str, Any]:
    try:
        payload = {
            "chat_history": chat_history
        }

        response = requests.post(
            f"{st.session_state.agent_url}/WeatherAgent/0.1",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "taAgwKey": st.session_state.ta_agw_key
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Agent request failed with status {response.status_code}: {response.text}"
            }

    except requests.exceptions.ConnectionError:
        return {
            "error": "Could not connect to weather agent. Make sure it's running on http://localhost:8000"
        }
    except requests.exceptions.Timeout:
        return {
            "error": "Request to weather agent timed out. Please try again."
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
                    formatted_lines.append(f"{TEMPERATURE_ICON} {line}")
                elif "city" in line.lower() or "location" in line.lower():
                    formatted_lines.append(f"{LOCATION_ICON} {line}")
                else:
                    formatted_lines.append(line)

            return '\n'.join(formatted_lines)
    except Exception:
        pass

    return response_text


def main():
    st.set_page_config(
        page_title="Weather Agent Chat",
        page_icon=WEATHER_ICON,
        layout="wide"
    )

    initialize_session_state()

    st.title(f"{WEATHER_ICON} Weather Agent Chat")
    st.markdown("Ask me about the weather in any city around the world!")

    with st.sidebar:
        st.header(f"{SETTINGS_ICON} Configuration")

        agent_url = st.text_input(
            "Weather Agent URL",
            value=st.session_state.agent_url,
            help="URL where the weather agent is running"
        )
        st.session_state.agent_url = agent_url

        ta_agw_key = st.text_input(
            "Kong Gateway Key (taAgwKey)",
            value=st.session_state.ta_agw_key,
            type="password",
            help="Authentication key for Kong gateway routing"
        )
        st.session_state.ta_agw_key = ta_agw_key

        st.header(f"{STATUS_ICON} Status")

        try:
            health_response = requests.get(f"{agent_url}/WeatherAgent/0.1/docs", timeout=5)
            if health_response.status_code == 200:
                st.success(f"{SUCCESS_ICON} Weather Agent is running")
            else:
                st.error(f"{ERROR_ICON} Weather Agent health check failed")
        except Exception:
            st.error(f"{ERROR_ICON} Cannot connect to Weather Agent")

        st.header(f"{EXAMPLES_ICON} Example Queries")
        st.markdown("""
        - "What's the weather in New York?"
        - "How's the weather in Tokyo today?"
        - "Tell me about the weather in London"
        - "What are the coordinates of Paris?"
        - "Is it raining in Seattle?"
        """)

        if st.button(f"{CLEAR_ICON} Clear Chat History"):
            st.session_state.messages = []
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
                    error_message = f"{ERROR_ICON} **Error:** {response['error']}"
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
                            st.caption(f"{TOKENS_ICON} Tokens used: {token_info.get('total_tokens', 'N/A')}")

                    except Exception as e:
                        error_message = f"{ERROR_ICON} **Error processing response:** {str(e)}"
                        st.markdown(error_message)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_message
                        })


if __name__ == "__main__":
    main()
