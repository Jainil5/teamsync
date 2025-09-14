# streamlit_slack_clone.py
# Streamlit communication app (Slack-like) using MongoDB
# Requirements: pip install streamlit pymongo python-dotenv streamlit-autorefresh

import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

# Load env
load_dotenv()

# ----------------------------------------------------------------------------
# MongoDB Connection Configuration
# ----------------------------------------------------------------------------
database_name = "TEAMSYNC"
collection_users = "USERS"
collection_messages = "MESSAGES"

# --- Helpers ---
@st.cache_resource
def get_db():
    client = MongoClient(mongo_uri)
    return client[database_name]

def verify_login(user_id, password):
    db = get_db()
    return db[collection_users].find_one({'user_id': user_id, 'password_hash': password})

def fetch_users():
    db = get_db()
    return list(db[collection_users].find({}, {'password_hash': 0}))

def fetch_messages(user_a, user_b, limit=200):
    db = get_db()
    q = {
        '$or': [
            {'sender_user_id': user_a, 'receiver_user_id': user_b},
            {'sender_user_id': user_b, 'receiver_user_id': user_a}
        ]
    }
    # Sort DESCENDING so newest messages come first
    msgs = list(db[collection_messages].find(q).sort('sent_at', -1).limit(limit))
    return msgs

def send_message(sender, receiver, content, team_id=0):
    db = get_db()
    message = {
        'message_id': f'msg_{uuid.uuid4().hex[:8]}',
        'sender_user_id': sender,
        'receiver_user_id': receiver,
        'team_id': team_id,
        'content': content,
        'translated': '',
        'sent_at': datetime.utcnow().isoformat() + 'Z'
    }
    db[collection_messages].insert_one(message)
    return message

# --- Streamlit UI ---
st.set_page_config(page_title='Slack-lite', layout='wide')

# Auto-refresh every 2.5 seconds to simulate realtime updates
st_autorefresh(interval=2500, limit=None, key="autorefresh")

if 'user' not in st.session_state:
    st.session_state.user = None

# Sidebar: Login or Profile
with st.sidebar:
    st.title('Slack-lite')
    if st.session_state.user is None:
        st.subheader('Login')
        user_id = st.text_input('User ID', key='login_user')
        password = st.text_input('Password', type='password', key='login_pass')
        if st.button('Login'):
            user = verify_login(user_id.strip(), password.strip())
            if user:
                st.session_state.user = user
                st.success(f"Welcome, {user.get('username')}")
            else:
                st.error('Invalid credentials')
        st.info('Use user_id and password as provided in database sample (e.g., user_1)')
    else:
        user = st.session_state.user
        st.image(user.get('profile_picture_url'), width=80)
        st.markdown(f"**{user.get('username')}**")
        st.caption(f"Role: {', '.join(user.get('role', []))}")
        if st.button('Logout'):
            st.session_state.user = None

# Main UI layout
if st.session_state.user is None:
    st.markdown('### Please login from the sidebar to continue')
    st.stop()

current_user = st.session_state.user['user_id']
users = [u for u in fetch_users() if u['user_id'] != current_user]

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown('### People')
    for u in users:
        cols = st.columns([0.25, 0.75])
        with cols[0]:
            st.image(u.get('profile_picture_url'), width=48)
        with cols[1]:
            if st.button(u.get('username'), key=f"u_{u['user_id']}"):
                st.session_state['chat_with'] = u['user_id']
            st.caption(u.get('role')[0] if u.get('role') else '')

with col2:
    chat_with = st.session_state.get('chat_with', users[0]['user_id'] if users else None)
    partner = next((x for x in users if x['user_id'] == chat_with), None)
    if partner is None:
        st.info('Select a user to start chatting')
        st.stop()

    # Header
    st.subheader(f"💬 Chat with {partner['username']}")
    st.caption(f"Language: {partner.get('primary_language')}")

    # Messages area (newest first)
    messages = fetch_messages(current_user, partner['user_id'])
    for m in messages:  # already newest first
        if m['sender_user_id'] == current_user:
            with st.chat_message("user", avatar=st.session_state.user.get('profile_picture_url')):
                st.write(m['content'])
                st.caption(m['sent_at'])
        else:
            with st.chat_message("assistant", avatar=partner.get('profile_picture_url')):
                st.write(m['content'])
                st.caption(m['sent_at'])

    # Chat input box
    if prompt := st.chat_input("Type your message here..."):
        send_message(current_user, partner['user_id'], prompt.strip())

    # Quick actions
    st.markdown('### Actions')
    a1, a2, a3 = st.columns(3)
    if a1.button('Send Hello'):
        send_message(current_user, partner['user_id'], 'Hello!')
    if a2.button('Get Briefing'):
        send_message(current_user, partner['user_id'], 'Can you send the briefings?')
    if a3.button('Mark Read'):
        st.success('Marked as read (UI only)')

# Footer
st.markdown('---')
