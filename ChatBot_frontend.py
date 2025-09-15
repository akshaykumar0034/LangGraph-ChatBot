import streamlit as st
from Chatbot_backend import chatbot
from langchain_core.messages import HumanMessage

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

# st.session_state -> dict ->
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


# Loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# {'role': 'assistant', 'content': 'HellO'}

user_input = st.chat_input('Type Here')

if user_input:

    # First add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    
    # 2. Stream assistant’s reply in real-time (not in history yet)
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content
            for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )

    # 3. After streaming ends, save assistant’s reply for future reruns
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
