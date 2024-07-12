import os
import json

import streamlit as st
import boto3

import pandas as pd
import uuid

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


# Initialize Bedrock agent Runtime client
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name="us-west-2")

# Streamlit app title
st.title("AWS Network Manager Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to invoke Bedrock agent
def invoke_bedrock_agent(prompt):
    response = bedrock_agent_runtime.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=SESSION_ID,
        inputText=prompt
    )
    return response

# Function to process and format the agent's response
def process_response(response):
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

# Accept user input
if prompt := st.chat_input("What would you like to know about your network?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = invoke_bedrock_agent(prompt)
        formatted_response = process_response(response)
        st.markdown(formatted_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": formatted_response})