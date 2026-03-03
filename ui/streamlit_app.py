"""
Streamlit UI for Agentic CoE Demo

A modern, interactive interface for demoing multi-agent AI systems.
"""

import streamlit as st  # type: ignore
import requests
import json
from typing import List, Dict, Any
import time
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Agentic CoE Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #0066CC;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    .tool-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        background-color: #0066CC;
        color: white;
        font-size: 0.8rem;
        margin: 0.2rem;
    }
    .message-user {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .message-assistant {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .handoff-indicator {
        background-color: #FFF3E0;
        padding: 0.5rem;
        border-left: 4px solid #FF9800;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = st.secrets.get("API_BASE_URL", "https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None
if "orchestration_mode" not in st.session_state:
    st.session_state.orchestration_mode = False
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []


def get_agents() -> List[Dict[str, Any]]:
    """Fetch list of available agents"""
    try:
        response = requests.get(f"{API_BASE_URL}/agents/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch agents: {str(e)}")
        return []


def chat_with_agent(agent_id: str, message: str) -> Dict[str, Any]:
    """Send message to specific agent"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/agents/{agent_id}/chat",
            json={
                "message": message,
                "context": {},
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to chat with agent: {str(e)}")
        return None


def orchestrate_agents(initial_agent_id: str, message: str, strategy: str) -> Dict[str, Any]:
    """Orchestrate multiple agents"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/orchestrate/",
            json={
                "message": message,
                "initial_agent_id": initial_agent_id,
                "context": {},
                "strategy": strategy,
                "max_iterations": 10
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to orchestrate agents: {str(e)}")
        return None


# Main UI
st.markdown('<div class="main-header">🤖 Agentic CoE Demo</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Mode selection
    mode = st.radio(
        "Select Mode",
        ["Single Agent", "Multi-Agent Orchestration"],
        index=0 if not st.session_state.orchestration_mode else 1
    )
    st.session_state.orchestration_mode = (mode == "Multi-Agent Orchestration")
    
    st.divider()
    
    # Fetch available agents
    agents = get_agents()
    
    if agents:
        st.subheader("📋 Available Agents")
        
        for agent in agents:
            with st.expander(f"🤖 {agent['agent_name']}"):
                st.write(f"**ID:** `{agent['agent_id']}`")
                st.write(f"**Description:** {agent['description']}")
                st.write(f"**Status:** {agent['status']}")
                
                if agent.get('capabilities'):
                    st.write("**Capabilities:**")
                    for cap in agent['capabilities']:
                        st.write(f"- {cap}")
                
                if agent.get('tools'):
                    st.write("**Tools:**")
                    for tool in agent['tools']:
                        st.markdown(f'<span class="tool-badge">{tool}</span>', unsafe_allow_html=True)
                
                if st.button(f"Select {agent['agent_name']}", key=f"select_{agent['agent_id']}"):
                    st.session_state.selected_agent = agent
                    st.success(f"Selected: {agent['agent_name']}")
    else:
        st.warning("No agents available. Please start the API server.")
    
    st.divider()
    
    # Orchestration settings
    if st.session_state.orchestration_mode:
        st.subheader("🔄 Orchestration Settings")
        orchestration_strategy = st.selectbox(
            "Strategy",
            ["sequential", "parallel", "conditional", "hierarchical"]
        )
        st.info("Multi-agent orchestration allows agents to collaborate and hand off tasks.")
    
    st.divider()
    
    # Clear conversation
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()
    
    # Demo scenarios
    st.subheader("💡 Demo Scenarios")
    if st.button("Customer Support Query"):
        st.session_state.demo_message = "I need help tracking my order #12345"
    if st.button("Technical Issue"):
        st.session_state.demo_message = "My application keeps crashing when I try to upload files"
    if st.button("Product Inquiry"):
        st.session_state.demo_message = "What are the features of your premium plan?"

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat Interface")
    
    # Display selected agent
    if st.session_state.selected_agent:
        agent = st.session_state.selected_agent
        st.info(f"🤖 Currently chatting with: **{agent['agent_name']}** | Status: {agent['status']}")
    else:
        st.warning("⚠️ Please select an agent from the sidebar")
    
    # Chat messages
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="message-user">
                    <strong>You:</strong><br>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                agent_name = msg.get("agent_name", "Agent")
                tools_used = msg.get("tools_used", [])
                handoff_to = msg.get("handoff_to")
                
                st.markdown(f"""
                <div class="message-assistant">
                    <strong>{agent_name}:</strong><br>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
                
                if tools_used:
                    st.markdown(f"**🔧 Tools used:** {', '.join(tools_used)}")
                
                if handoff_to:
                    st.markdown(f"""
                    <div class="handoff-indicator">
                        ↪️ <strong>Handed off to:</strong> {handoff_to}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Type your message here..." if st.session_state.selected_agent else "Select an agent first...")
    
    # Handle demo message
    if "demo_message" in st.session_state:
        user_input = st.session_state.demo_message
        del st.session_state.demo_message
    
    if user_input and st.session_state.selected_agent:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Show processing
        with st.spinner("🤔 Agent is thinking..."):
            if st.session_state.orchestration_mode:
                # Multi-agent orchestration
                result = orchestrate_agents(
                    st.session_state.selected_agent["agent_id"],
                    user_input,
                    orchestration_strategy
                )
                
                if result:
                    # Add all agent responses
                    for response in result.get("responses", []):
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response["content"],
                            "agent_name": response["agent_name"],
                            "tools_used": response.get("tools_used", []),
                            "handoff_to": response.get("handoff_to")
                        })
            else:
                # Single agent chat
                response = chat_with_agent(
                    st.session_state.selected_agent["agent_id"],
                    user_input
                )
                
                if response:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["content"],
                        "agent_name": response["agent_name"],
                        "tools_used": response.get("tools_used", []),
                        "handoff_to": response.get("handoff_to")
                    })
        
        st.rerun()

with col2:
    st.header("📊 Analytics")
    
    # Message statistics
    total_messages = len(st.session_state.messages)
    user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
    agent_messages = total_messages - user_messages
    
    st.metric("Total Messages", total_messages)
    st.metric("User Messages", user_messages)
    st.metric("Agent Responses", agent_messages)
    
    st.divider()
    
    # Tool usage
    st.subheader("🔧 Tool Usage")
    all_tools = []
    for msg in st.session_state.messages:
        if msg.get("tools_used"):
            all_tools.extend(msg["tools_used"])
    
    if all_tools:
        tool_counts = {}
        for tool in all_tools:
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        for tool, count in tool_counts.items():
            st.write(f"**{tool}:** {count} times")
    else:
        st.info("No tools used yet")
    
    st.divider()
    
    # Export conversation
    st.subheader("💾 Export")
    if st.button("📄 Export as JSON"):
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "mode": "orchestration" if st.session_state.orchestration_mode else "single",
            "agent": st.session_state.selected_agent["agent_name"] if st.session_state.selected_agent else None,
            "messages": st.session_state.messages
        }
        st.download_button(
            label="Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    Agentic CoE - Production-Ready Multi-Agent AI System | v1.0.0
</div>
""", unsafe_allow_html=True)
