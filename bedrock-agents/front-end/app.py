import os
import streamlit as st
import boto3
import json
import pandas as pd
import uuid
import time


from dotenv import load_dotenv


load_dotenv()


REGION = os.getenv("REGION")
AWS_ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN=os.getenv("AWS_SESSION_TOKEN")
AGENT_ID = os.getenv("AGENT_ID")
AGENT_ALIAS_ID = os.getenv("AGENT_ALIAS_ID")
SESSION_ID = os.getenv("SESSION_ID")



# Authenticate to AWS
boto3.setup_default_session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name='us-east-1'
)

# Set page config
st.set_page_config(page_title="AWS Network Manager Assistant", page_icon="🌐", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .main {
        background: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for configuration
st.sidebar.header("Configuration")
agent_id = st.sidebar.text_input("Agent ID", value=AGENT_ID)
agent_alias_id = st.sidebar.text_input("Agent Alias ID", value=AGENT_ALIAS_ID)
region_name = st.sidebar.text_input("AWS Region", value="us-west-2")

# Initialize Bedrock Agent Runtime client
@st.cache_resource
def get_bedrock_client():
    return boto3.client('bedrock-agent-runtime', region_name=region_name)

bedrock_agent_runtime = get_bedrock_client()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Function to invoke Bedrock agent
def invoke_bedrock_agent(prompt):
    try:
        start_time = time.time()
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=st.session_state.session_id,
            inputText=prompt
        )
        end_time = time.time()
        response_time = end_time - start_time
        return response, response_time
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    return None

# Function to process and format the agent's response
def process_response(response):
    if response is None:
        return "Sorry, I couldn't process your request. Please check the configuration and try again."
    
    full_response = ""
    for event in response['completion']:
        if 'chunk' in event:
            chunk = event['chunk']
            if 'bytes' in chunk:
                full_response += chunk['bytes'].decode('utf-8')
    
    # Try to parse as JSON
    try:
        json_response = json.loads(full_response)
        if isinstance(json_response, list) and len(json_response) > 0 and isinstance(json_response[0], dict):
            df = pd.DataFrame(json_response)
            return df.to_markdown()
    except json.JSONDecodeError:
        pass
    
    # Check if the response is code
    if full_response.strip().startswith('```'):
        return full_response
    
    # Otherwise, return as plain text
    return full_response

# Main app layout
st.title("🌐 AWS Network Manager Assistant")

# Two-column layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Chat")
    chat_container = st.container()

with col2:
    st.subheader("Session Info")
    st.info(f"Session ID: {st.session_state.session_id}")
    st.success(f"Agent Status: Active" if agent_id and agent_alias_id else "Agent Status: Not Configured")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.experimental_rerun()

# Display chat messages
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
        if "response_time" in message:
            st.caption(f"Response time: {message['response_time']:.2f} seconds")


# User input
user_input = st.chat_input("What would you like to know about your network?")

if user_input:
    if not agent_id or not agent_alias_id:
        st.error("Please configure the Agent ID and Agent Alias ID in the sidebar.")
    else:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
        
        # Show loading spinner
        with st.spinner("Thinking..."):
            response, response_time = invoke_bedrock_agent(user_input)
            formatted_response = process_response(response)
        
        # Display assistant response
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(formatted_response)
                st.caption(f"Response time: {response_time:.2f} seconds")
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": formatted_response,
            "response_time": response_time
            })

# Display a hint for first-time users
if not st.session_state.messages:
    st.info("👋 Welcome! Ask me anything about your AWS Network Manager setup.")
