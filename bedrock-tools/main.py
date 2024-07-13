from chat_engine import chat, print_conversation
from bedrock_utils import initialize_bedrock_client
from tools import get_all_tools



def main():
    bedrock_client = initialize_bedrock_client()
    tools = get_all_tools()
    messages = []
    
    print("Welcome to the AWS Network Assistant. You can ask about VPCs, Internet Gateways, NAT Gateways, Route Tables, and other network components.")
    print("Type 'exit', 'quit', or 'bye' to end the conversation.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break
        chat(user_input, messages, bedrock_client, tools)
    
    print("\nFinal Conversation History:")
    print_conversation(messages)


if __name__ == "__main__":
    main()