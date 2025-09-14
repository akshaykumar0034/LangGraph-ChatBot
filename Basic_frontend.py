import streamlit as st

with st.chat_message('User'):
    st.text("Hi")

with st.chat_message('Assistant'):
    st.text("How can I help you ?")

with st.chat_message('user'):
    st.text('My Name is Aerin')

user_input = st.chat_input('Type here')

if user_input:
    with st.chat_message('user'):
        st.text(user_input)