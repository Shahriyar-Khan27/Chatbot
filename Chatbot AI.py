import os
import streamlit as st
import groq

# Initialize the Groq client with your API key
client = groq.Client(api_key="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")

def get_llm_response(input_text, conversation_history=None):
    if conversation_history is None:
        conversation_history = []
    
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
        
        # Make the API call to Groq
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # You can change this to another available model
            messages=messages,
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        st.error(f"Error calling Groq API: {str(e)}")
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
        
        # Check if user wants to end the conversation
        if any(goodbye in user_input.lower() for goodbye in ["goodbye", "bye", "see you", "exit", "quit"]):
            st.write("Thank you for chatting with me. Have a great day!")

if __name__ == '__main__':
    main()