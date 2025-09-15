import streamlit as st
from db_manager import get_users_data, get_user_name,get_chat_history, get_user_id, add_message
from datetime import datetime
import time

st.set_page_config(page_title="TeamSync", page_icon=":speech_balloon:", layout="wide")

user_id = "user_1"
user_name = get_user_name(user_id)
welcome_text = f"Hello, {user_name} !"
user_list = get_users_data(user_id)
main_list = ["HOME"]
main_list.extend(user_list.values())

st.sidebar.title(welcome_text)
st.sidebar.title("- - - - - - - - - -")

to = st.sidebar.radio(label = "Direct Messages:",options=main_list)

if to == "HOME":
    st.title(welcome_text)
    st.header("Welcome to TeamSync , your AI-powered collaborative workspace!")
else :   
        col1, col2, col3= st.columns(3, gap="medium")
        with col1:
            st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=70)
        with col2:
            st.header(f"{to}")
              
            
        with st.container(height=300, gap="small"):
            to_id = get_user_id(to)
            message_list = get_chat_history(user_id, to_id)
            for message in message_list:
                if message["content"] is not None and message["content"].strip() != "":
                    if message["sender_user_id"] == user_id:
                        c1 , c2 = st.columns(2)
                        with c2:
                                with st.chat_message("user"):
                                    st.write(message["content"])
                    else:
                        c1 , c2 = st.columns(2)
                        with c1:
                            with st.chat_message("user",avatar="https://cdn-icons-png.flaticon.com/512/149/149071.png"):
                                st.write(message["content"])
                    
        input = st.chat_input("Type your message here...")
        if input:
            add_message(user_id, to_id, input)    
            st.rerun()

# time.sleep(1)
# st.rerun()
        