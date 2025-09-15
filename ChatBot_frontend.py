# ----------------------------- Imports -----------------------------
import streamlit as st
from Chatbot_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# ----------------------------- Utility Functions -----------------------------

def generate_thread_id():
    """Generate a unique identifier (UUID) for a new chat thread."""
    return uuid.uuid4()

def add_thread(thread_id):
    """Add a thread ID to session state list if it doesn't exist."""
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    """
    Loads the conversation messages from the backend for a given thread ID.
    Returns a list of BaseMessage objects. If no messages exist, returns [].
    """
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

def generate_thread_name_from_messages(messages, max_words=10):
    """Generate/update a friendly thread name based on conversation messages."""
    if not messages:
        return "New Chat"
    for msg in messages:
        if isinstance(msg, HumanMessage):
            words = msg.content.split()[:max_words]
            return " ".join(words)
    return " ".join(messages[0].content.split()[:max_words])

def reset_chat():
    """
    Clears the current chat without creating a new thread yet.
    A new thread will be created when the first user message is typed.
    """
    st.session_state['message_history'] = []
    st.session_state['thread_id'] = None

# ----------------------------- Session Setup -----------------------------

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

if 'thread_names' not in st.session_state:
    st.session_state['thread_names'] = {}

# ----------------------------- Sidebar UI -----------------------------
st.sidebar.title('LangGraph ChatBot')

# Button to start new chat (just reset, no thread created yet)
if st.sidebar.button('New Chat'):
    reset_chat()

# Display past conversation threads with friendly names
for thread_id in st.session_state['chat_threads'][::-1]:
    if thread_id not in st.session_state['thread_names']:
        messages = load_conversation(thread_id)
        st.session_state['thread_names'][thread_id] = generate_thread_name_from_messages(messages)

    thread_name = st.session_state['thread_names'][thread_id]

    if st.sidebar.button(thread_name, key=str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)
        temp_messages = []
        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})
        st.session_state['message_history'] = temp_messages

# ----------------------------- Display Conversation -----------------------------
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# ----------------------------- Chat Input -----------------------------
user_input = st.chat_input('Type Here')

# ----------------------------- Handle New User Message -----------------------------
if user_input:
    # If no active thread, create one now
    if st.session_state['thread_id'] is None:
        thread_id = generate_thread_id()
        st.session_state['thread_id'] = thread_id
        add_thread(thread_id)
        st.session_state['thread_names'][thread_id] = user_input  # use first message as name

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    # 1. Append user message
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # 2. Stream AI response
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content
            for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )

    # 3. Append assistant message
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})

    # 4. Update thread name dynamically
    current_messages = []
    for m in st.session_state['message_history']:
        if m['role'] == 'user':
            current_messages.append(HumanMessage(content=m['content']))
        else:
            current_messages.append(AIMessage(content=m['content']))
    st.session_state['thread_names'][st.session_state['thread_id']] = generate_thread_name_from_messages(current_messages)
