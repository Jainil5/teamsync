# pages/1_Chat.py
import streamlit as st
from pymongo import MongoClient
from datetime import datetime

# -----------------------
# MongoDB Connection
# -----------------------
database_name = "TEAMSYNC"
collection_users = "USERS"
collection_messages = "MESSAGES"
try:
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        print("Connection to MongoDB successful.")
        
except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

main_db = client[database_name]
users_db = main_db[collection_users]
messages_db = main_db[collection_messages]

st.set_page_config(page_title="teamsync — Chat", page_icon="💬", layout="wide")

# -----------------------
# Auth Check
# -----------------------
if "teamsync_logged_in" not in st.session_state or not st.session_state["teamsync_logged_in"]:
    st.error("🚨 Please log in first from the login page!")
    st.stop()

user_id = st.session_state["user_id"]

st.title(f"💬 teamsync Chat — {user_id}")

# -----------------------
# Fetch Messages
# -----------------------
messages = list(messages_db.find().sort("timestamp", -1))  # latest first

st.subheader("Chat History")
for msg in messages:
    sender = msg.get("sender")
    text = msg.get("text")
    ts = msg.get("timestamp")
    if sender == user_id:
        st.markdown(f"<div style='text-align:right; color:blue;'>🧑‍💻 {sender}: {text} <br><span style='font-size:10px;'>{ts}</span></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align:left; color:green;'>👥 {sender}: {text} <br><span style='font-size:10px;'>{ts}</span></div>", unsafe_allow_html=True)

# -----------------------
# Send New Message
# -----------------------
st.subheader("Send a message")
with st.form("send_message"):
    msg_text = st.text_input("Type your message here...")
    send = st.form_submit_button("Send")

    if send and msg_text.strip():
        messages_db.insert_one({
            "sender": user_id,
            "text": msg_text.strip(),
            "timestamp": datetime.now()
        })

# -----------------------
# Logout
# -----------------------
if st.button("🚪 Logout"):
    st.session_state.clear()
