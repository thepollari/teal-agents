import json
import os
import requests
import streamlit as st
from typing import Dict, List


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_url" not in st.session_state:
        st.session_state.agent_url = "http://localhost:8000"


def format_university_data(universities: List[Dict]) -> str:
    """Format university data for display in chat."""
    if not universities:
        return "No universities found."
    
    formatted_text = ""
    for i, uni in enumerate(universities, 1):
        formatted_text += f"\n**{i}. {uni.get('name', 'Unknown University')}**\n"
        formatted_text += f"🌍 **Country:** {uni.get('country', 'Unknown')}"
        
        if uni.get('state_province'):
            formatted_text += f", {uni.get('state_province')}"
        formatted_text += "\n"
        
        if uni.get('web_pages'):
            formatted_text += f"🔗 **Website:** {uni.get('web_pages')[0]}\n"
        
        if uni.get('domains'):
            formatted_text += f"📧 **Domain:** {uni.get('domains')[0]}\n"
        
        formatted_text += "\n"
    
    return formatted_text


def call_university_agent(message: str, chat_history: List[Dict]) -> str:
    """Call the university agent API."""
    try:
        payload = {
            "chat_history": chat_history
        }
        
        response = requests.post(
            f"{st.session_state.agent_url}/UniversityAgent/0.1",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("output_raw", "No response from agent")
        else:
            return f"Error: Agent returned status code {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "❌ **Connection Error**: Could not connect to the university agent. Please ensure the agent is running on http://localhost:8000"
    except requests.exceptions.Timeout:
        return "⏱️ **Timeout Error**: The agent took too long to respond. Please try again."
    except Exception as e:
        return f"❌ **Error**: {str(e)}"


def check_agent_status() -> bool:
    """Check if the university agent is running."""
    try:
        response = requests.get(f"{st.session_state.agent_url}/UniversityAgent/0.1/docs", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    st.set_page_config(
        page_title="University Agent Chat",
        page_icon="🎓",
        layout="wide"
    )
    
    initialize_session_state()
    
    st.title("🎓 University Agent Chat")
    st.markdown("*Powered by Google Gemini and Universities API*")
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        agent_url = st.text_input(
            "Agent URL",
            value=st.session_state.agent_url,
            help="URL where the university agent is running"
        )
        if agent_url != st.session_state.agent_url:
            st.session_state.agent_url = agent_url
        
        st.header("📊 Status")
        if st.button("Check Agent Status"):
            if check_agent_status():
                st.success("✅ Agent is running")
            else:
                st.error("❌ Agent is not responding")
        
        st.header("💡 Example Queries")
        example_queries = [
            "Find universities in Finland",
            "Search for Aalto University",
            "What universities are in Japan?",
            "Tell me about MIT",
            "Universities in Germany"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{query}"):
                st.session_state.messages.append({"role": "user", "content": query})
                st.rerun()
        
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
    
    st.header("💬 Chat with University Agent")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                content = message["content"]
                try:
                    if "universities" in content and content.strip().startswith("{"):
                        data = json.loads(content)
                        if "universities" in data:
                            st.markdown(data.get("message", ""))
                            if data["universities"]:
                                formatted_unis = format_university_data(data["universities"])
                                st.markdown(formatted_unis)
                            else:
                                st.markdown("No universities found for your query.")
                        else:
                            st.markdown(content)
                    else:
                        st.markdown(content)
                except (json.JSONDecodeError, KeyError):
                    st.markdown(content)
            else:
                st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about universities..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Searching universities..."):
                chat_history = []
                for msg in st.session_state.messages:
                    chat_history.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                
                response = call_university_agent(prompt, chat_history)
                
                try:
                    if response.strip().startswith("{") and "universities" in response:
                        data = json.loads(response)
                        if "universities" in data:
                            st.markdown(data.get("message", ""))
                            if data["universities"]:
                                formatted_unis = format_university_data(data["universities"])
                                st.markdown(formatted_unis)
                            else:
                                st.markdown("No universities found for your query.")
                        else:
                            st.markdown(response)
                    else:
                        st.markdown(response)
                except (json.JSONDecodeError, KeyError):
                    st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.markdown("---")
    st.markdown("""
    **How to use:**
    1. Make sure the University Agent is running on http://localhost:8000
    2. Ask questions about universities, countries, or specific institutions
    3. Use the example queries in the sidebar to get started
    
    **Setup Instructions:**
    ```bash
    cd ~/repos/teal-agents/src/sk-agents
    export GEMINI_API_KEY="your_api_key"
    export TA_SERVICE_CONFIG="../../orchestrators/assistant-orchestrator/example/university/config.yaml"
    export TA_PLUGIN_MODULE="../../orchestrators/assistant-orchestrator/example/university/custom_plugins.py"
    export TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE="sk_agents.chat_completion.custom.gemini_chat_completion_factory"
    export TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME="GeminiChatCompletionFactory"
    uv run uvicorn sk_agents.app:app --host 0.0.0.0 --port 8000
    
    cd ~/repos/teal-agents/src/orchestrators/assistant-orchestrator/example/university
    uv run streamlit run streamlit_ui.py
    ```
    """)


if __name__ == "__main__":
    main()
