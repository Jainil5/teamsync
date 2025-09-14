# team_chat_app.py
# Run: streamlit run team_chat_app.py --server.port 8501

import streamlit as st
from pymongo import MongoClient
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# MongoDB connection
mongo_uri = "mongodb+srv://jainiljp72525:messi%401010@users.9tdxb.mongodb.net/"
database_name = "TEAMSYNC"
collection_users = "USERS"
collection_messages = "MESSAGES"

try:
    client = MongoClient(mongo_uri)
    client.admin.command("ping")
    print("✅ Connected to MongoDB")
except Exception as e:
    st.error(f"❌ Failed to connect MongoDB: {e}")

main_db = client[database_name]
users_db = main_db[collection_users]
messages_db = main_db[collection_messages]

# Fetch all users
def get_users():
    return list(users_db.find({}, {"_id": 0, "user_id": 1, "username": 1}))

# Fetch messages for a user
def get_messages(user_id):
    return list(messages_db.find({"user_id": user_id}).sort("timestamp", -1))

# Add new message
def add_message(user_id, message):
    messages_db.insert_one({
        "user_id": user_id,
        "message": message,
        "timestamp": datetime.utcnow()
    })

# Sidebar users
users = get_users()

# Parse user_id from URL query params
query_params = st.query_params
default_user = query_params.get("user_id", [None])[0]

user_list = {u["username"]: u["user_id"] for u in users}

selected_username = st.sidebar.radio("👥 Select User", list(user_list.keys()))

selected_user_id = user_list[selected_username]

# Update URL query param for bookmarking
st.query_params["user_id"] = selected_user_id

# Display chat messages
st.title(f"💬 Chat - {selected_username}")

messages = get_messages(selected_user_id)

if not messages:
    st.info("No messages yet. Start the conversation!")

for msg in messages:
    with st.chat_message("user"):
        st.write(msg["message"])
        st.caption(f"🕒 {msg['timestamp']}")

# Input box for new message
new_msg = st.chat_input("Type your message...")
if new_msg:
    add_message(selected_user_id, new_msg)
    st.rerun()
