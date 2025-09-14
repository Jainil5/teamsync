"""
Streamlit Slack-like Team Chat (MongoDB)
- Shows users from USERS collection
- Shows messages from MESSAGES collection in DESCENDING order so latest message appears first
- Simple send-message (inserts into MESSAGES)
- Compact, clean UI with avatars and message bubbles
Requirements:
pip install streamlit pymongo python-dotenv
Set environment variable MONGO_URL to your MongoDB connection string
"""
import streamlit as st
from pymongo import MongoClient, DESCENDING
from datetime import datetime, timezone
import os
import html

# ---------------------------
# Configuration
# ---------------------------
DB_NAME = os.environ.get("DB_NAME", "TEAMSYNC")

# ---------------------------
# Helpers
# ---------------------------
@st.cache_resource
def get_db():
    client = MongoClient(MONGO_URL)
    return client[DB_NAME]

def iso_now_z():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def safe(s):
    return html.escape(str(s))

def get_users(db):
    coll = db["USERS"]
    docs = list(coll.find({}, {"_id": 1, "user_id": 1, "username": 1, "profile_picture_url": 1, "role": 1, "last_active_at": 1}))
    # sort by username for display
    docs.sort(key=lambda d: d.get("username","").lower())
    return docs

def get_messages_between(db, u1, u2, team_id=None, limit=200):
    coll = db["MESSAGES"]
    # Query for messages either direction between u1 and u2
    q = {
        "$or": [
            {"sender_user_id": u1, "receiver_user_id": u2},
            {"sender_user_id": u2, "receiver_user_id": u1}
        ]
    }
    if team_id is not None:
        q["team_id"] = team_id
    # We assume sent_at is ISO8601 strings; lexical sort on ISO works correctly -> newest first
    cursor = coll.find(q).sort("sent_at", DESCENDING).limit(limit)
    return list(cursor)

def get_team_messages(db, team_id=0, limit=200):
    coll = db["MESSAGES"]
    cursor = coll.find({"team_id": team_id}).sort("sent_at", DESCENDING).limit(limit)
    return list(cursor)

def insert_message(db, sender_id, receiver_id, content, team_id=0):
    coll = db["MESSAGES"]
    doc = {
        "message_id": f"msg_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "sender_user_id": sender_id,
        "receiver_user_id": receiver_id,
        "team_id": team_id,
        "content": content,
        "translated": "",
        "sent_at": iso_now_z()
    }
    coll.insert_one(doc)
    return doc

# ---------------------------
# Styling
# ---------------------------
st.set_page_config(page_title="TeamSync — Streamlit Chat", layout="wide")
st.markdown(
    """
<style>
body { background: linear-gradient(180deg,#f7fbf9,#ffffff); }
.chat-container { padding: 16px; border-radius: 12px; box-shadow: 0 6px 16px rgba(16,24,40,.08); background: white; }
.user-list { max-height: 70vh; overflow: auto; padding: 8px; }
.avatar { width:44px;height:44px;border-radius:12px;object-fit:cover; }
.msg-row { display:flex; margin: 8px 0; align-items:flex-start; gap:8px; }
.msg-bubble { max-width:70%; padding:10px 14px; border-radius:12px; line-height:1.3; font-size:14px; }
.msg-left { background: #f1f6f4; border-top-left-radius:4px; }
.msg-right { background: #A5C9A4; color: #04260F; margin-left:auto; border-top-right-radius:4px; }
.username { font-weight:600; font-size:13px; margin-bottom:4px; color:#03271B; }
.timestamp { font-size:11px; color:#667085; margin-top:6px; }
.header { display:flex; align-items:center; gap:12px; padding:12px 0; border-bottom:1px solid #eef3ee; }
.search-input { width:100%; padding:8px; border-radius:8px; border:1px solid #e6efe7; }
.small-muted { font-size:12px; color:#7b8a80; }
.send-row { display:flex; gap:8px; align-items:center; }
.send-input { flex:1; }
</style>
""", unsafe_allow_html=True
)

# ---------------------------
# App Layout
# ---------------------------
db = get_db()

left_col, center_col, right_col = st.columns([1.6, 3.5, 1.6])

with left_col:
    st.markdown("## 👥 Team members")
    users = get_users(db)
    # Search box
    q = st.text_input("Search users...", key="user_search")
    filtered = [u for u in users if q.lower() in u.get("username","").lower() or q.lower() in " ".join(u.get("role",[])).lower()]
    # current user select
    st.markdown("**Select your user**")
    user_options = {u["username"]: u for u in users}
    if "current_user" not in st.session_state:
        # default to first user if exists
        st.session_state.current_user = users[0]["user_id"] if users else ""
    # map display -> user_id
    display_names = [u["username"] for u in filtered] if filtered else [u["username"] for u in users]
    sel_username = st.selectbox("", display_names, index=0 if display_names else 0, key="sel_user_select")
    current_user = user_options.get(sel_username, user_options.get(list(user_options.keys())[0], {})).get("user_id","")
    st.session_state.current_user = current_user

    st.markdown("---")
    st.markdown("**Quick contacts**")
    st.write("")  # spacer
    # Show list with avatars
    for u in filtered[:40]:
        is_active = u.get("last_active_at", "")
        col1, col2 = st.columns([0.2, 3.8])
        with col1:
            st.image(u.get("profile_picture_url", ""), width=44)
        with col2:
            st.markdown(f"**{safe(u.get('username',''))}**  <div class='small-muted'>{', '.join(u.get('role',[]))}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("Tip: Messages display newest first (descending).")

with center_col:
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    # Chat header & conversation selection
    st.markdown("<div class='header'>", unsafe_allow_html=True)
    st.markdown(f"<div style='flex:1'><h3 style='margin:0'>Team Chat</h3><div class='small-muted'>Team-wide channel (team_id=0) - newest messages at top</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Option: show team channel or 1:1
    mode = st.radio("View", ["Team Channel", "1:1 Conversation"], index=0)
    if mode == "1:1 Conversation":
        # choose other user
        other_usernames = [u["username"] for u in users if u["user_id"] != st.session_state.current_user]
        selected_other = st.selectbox("Chat with", other_usernames)
        other_user_id = user_options[selected_other]["user_id"]
        messages = get_messages_between(db, st.session_state.current_user, other_user_id, team_id=0, limit=400)
    else:
        other_user_id = None
        messages = get_team_messages(db, team_id=0, limit=400)

    # Control: reverse or keep newest first
    newest_first = st.checkbox("Show newest first (descending)", value=True)
    if not newest_first:
        messages = list(reversed(messages))

    # Messages container (we'll display in the order of 'messages' list)
    container = st.container()
    # show "no messages" if none
    if not messages:
        container.info("No messages yet.")
    else:
        for msg in messages:
            # fetch sender info
            sender = next((u for u in users if u["user_id"] == msg.get("sender_user_id")), None)
            sender_name = sender.get("username", msg.get("sender_user_id")) if sender else msg.get("sender_user_id")
            avatar = sender.get("profile_picture_url", "") if sender else ""
            ts = msg.get("sent_at", "")
            content = safe(msg.get("content", ""))
            # alignment: right if current user sent
            is_me = (msg.get("sender_user_id") == st.session_state.current_user)
            # build HTML for single message
            if is_me:
                html_msg = f"""
                <div class='msg-row' style='justify-content:flex-end;'>
                    <div style='max-width:76%; text-align:right;'>
                        <div class='msg-bubble msg-right'>{content}</div>
                        <div class='timestamp'>{safe(sender_name)} • {safe(ts)}</div>
                    </div>
                    <img class='avatar' src='{avatar}'/>
                </div>
                """
            else:
                html_msg = f"""
                <div class='msg-row'>
                    <img class='avatar' src='{avatar}'/>
                    <div style='max-width:76%;'>
                        <div class='username'>{safe(sender_name)}</div>
                        <div class='msg-bubble msg-left'>{content}</div>
                        <div class='timestamp'>{safe(ts)}</div>
                    </div>
                </div>
                """
            container.markdown(html_msg, unsafe_allow_html=True)

    # Sending new message
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex;align-items:center;gap:8px'>", unsafe_allow_html=True)
    # input fields
    with st.form("send_message_form", clear_on_submit=True):
        cols = st.columns([1, 0.28])
        with cols[0]:
            msg_input = st.text_area("Write a message", placeholder="Type message and press Send...", key="message_input", height=80)
        with cols[1]:
            st.write("")  # spacer
            send_btn = st.form_submit_button("Send")
        if send_btn:
            if not msg_input.strip():
                st.warning("Enter a message before sending.")
            else:
                # determine receiver (team or other)
                if mode == "1:1 Conversation":
                    receiver = other_user_id
                else:
                    receiver = None  # team channel: we keep receiver_user_id None or team messages can set receiver_user_id = '' or team_id only
                    # For simplicity we'll set receiver_user_id to current_user (so there is a sender/receiver pair) - but better is receiver_user_id = 'team_0'
                    receiver = st.session_state.current_user  # not actually used by team viewers but preserves schema
                inserted = insert_message(db, st.session_state.current_user, receiver, msg_input, team_id=0)
                st.success("Message sent.")
                # refresh page to show newest message at top

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # close chat-container

with right_col:
    st.markdown("## 🧾 Conversation Info")
    st.markdown(f"**Logged in as:** {safe(sel_username)}")
    st.markdown(f"**User ID:** {safe(st.session_state.current_user)}")
    st.markdown("---")
    st.markdown("### Recent activity")
    recent = sorted(users, key=lambda u: u.get("last_active_at",""), reverse=True)[:6]
    for u in recent:
        st.markdown(f"- {safe(u.get('username'))} • <span class='small-muted'>{safe(u.get('last_active_at',''))}</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Controls")
    st.write("- Toggle newest-first")
    st.write("- Use search to filter users")
    st.write("- This demo uses simple insertion; in production add auth + validation.")

