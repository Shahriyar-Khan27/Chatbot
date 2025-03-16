import os
import streamlit as st
from dotenv import load_dotenv
import httpx
import time

# Try to load environment variables
load_dotenv()

# Set page config first
st.set_page_config(page_title="Chatbot by Shahriyar Khan", page_icon="💬")

# Function to initialize Groq client safely
def initialize_groq_client():
    try:
        import groq
        api_key = os.environ.get("GROQ_API_KEY", "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")
        return groq.Client(api_key=api_key)
    except ImportError:
        st.error("The 'groq' package is not installed. Please install it using: pip install groq")
        st.stop()
    except Exception as e:
        st.error(f"Error initializing Groq client: {str(e)}")
        st.info("Try installing the required dependencies: pip install groq httpx")
        st.stop()

# Initialize client inside a function to handle errors better
@st.cache_resource
def get_client():
    return initialize_groq_client()

# Get a response from the LLM
def get_llm_response(input_text, conversation_history=None):
    if conversation_history is None:
        conversation_history = []
    
    client = get_client()
    
    # Create a system prompt
    system_prompt = """You are a helpful AI assistant in a chat application. 
    You should respond to user queries in a friendly and informative manner.
    Keep your responses concise (1-3 sentences unless detailed information is requested).
    If the user says goodbye or thanks you, respond appropriately and be polite.
    """
    
    try:
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for exchange in conversation_history:
            messages.append({"role": "user", "content": exchange["user"]})
            if "assistant" in exchange:
                messages.append({"role": "assistant", "content": exchange["assistant"]})
        
        # Add current user input
        messages.append({"role": "user", "content": input_text})
        
        # Make the API call to Groq with proper error handling and timeout
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=messages,
                    max_tokens=800,
                    temperature=0.7,
                    timeout=httpx.Timeout(30.0, connect=10.0)
                )
                return response.choices[0].message.content
            except httpx.TimeoutException:
                return "I'm sorry, the request timed out. Please try again with a shorter message or try later."
            except Exception as e:
                st.error(f"Error calling Groq API: {str(e)}")
                return "I'm sorry, I'm having trouble generating a response. Please try again in a moment."
    
    except Exception as e:
        st.error(f"Error preparing request: {str(e)}")
        return "I'm sorry, I'm having trouble understanding. Could you rephrase that?"

# Initialize session state
def init_session_state():
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def main():
    st.title("Chatbot (Made by Shahriyar Khan)")
    st.write("Welcome to the chatbot. Please type a message and press Enter to start the conversation.")
    
    # Initialize session state
    init_session_state()
    
    # Add a button to clear chat history
    if st.sidebar.button("Clear Conversation"):
        st.session_state.conversation_history = []
        st.session_state.messages = []
        st.experimental_rerun()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Get user input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get response
        response = get_llm_response(user_input, st.session_state.conversation_history)
        
        # Update conversation history
        st.session_state.conversation_history.append({
            "user": user_input,
            "assistant": response
        })
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # No need for the goodbye check since it's handled by the LLM via system prompt

if __name__ == '__main__':
    main()
