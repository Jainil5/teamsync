import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

API_BASE = "http://localhost:8000"

AI_CHAT_NAME = "🤖 TeamSync Agent"
AI_USER_ID = "0"
EVENTS_SECTION = "📅 Events"
SMART_REVIEW_SECTION = "📝 Smart Review"

st.set_page_config(
    page_title="TeamSync",
    page_icon="🤖",
    layout="wide"
)

st_autorefresh(interval=20_000, key="refresh")


def api_get(path):
    try:
        res = requests.get(f"{API_BASE}{path}", timeout=30)
        return res.json() if res.status_code == 200 else None
    except Exception:
        return None


def api_post(path, payload):
    try:
        res = requests.post(f"{API_BASE}{path}", json=payload, timeout=120)
        return res.json() if res.status_code == 200 else None
    except Exception:
        return None


if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = "user_1"

if "selected_chat" not in st.session_state:
    st.session_state.selected_chat = AI_CHAT_NAME

if "temp_messages" not in st.session_state:
    st.session_state.temp_messages = []

if "pending_ai_message" not in st.session_state:
    st.session_state.pending_ai_message = None

if "awaiting_ai_response" not in st.session_state:
    st.session_state.awaiting_ai_response = False

CURRENT_USER_ID = st.session_state.current_user_id


user_name = api_get(f"/users/name/{CURRENT_USER_ID}")["username"]

st.sidebar.markdown(
    f"""
    <div style="display:flex;gap:12px;align-items:center;padding:10px 5px;">
        <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png"
             style="width:42px;height:42px;border-radius:50%;">
        <div>
            <div style="font-size:16px;font-weight:600;">{user_name}</div>
            <div style="font-size:12px;color:gray;">Online</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    ### 🤖 TeamSync AIß
    **Multipurpose Enterprise AI Assistant**

    **Capabilities**
    - 🧠 Smart Reviews & Analysis  
    - 🗄 SQL Query Generation  
    - 📄 Policy & Project RAG  
    - 📁 DAM File Search  

    _Designed for internal teams, ops, and analytics._
    """
)

with st.sidebar.expander("⚙️ Options", expanded=False):
    users = api_get(f"/users/{CURRENT_USER_ID}") or {}

    user_map = {CURRENT_USER_ID: user_name}
    user_map.update(users)

    selected_user = st.selectbox(
        "Switch user (hidden)",
        options=list(user_map.keys()),
        format_func=lambda x: user_map[x],
        label_visibility="collapsed"
    )

    if selected_user != CURRENT_USER_ID:
        st.session_state.current_user_id = selected_user
        st.session_state.selected_chat = AI_CHAT_NAME
        st.session_state.temp_messages = []
        st.session_state.pending_ai_message = None
        st.session_state.awaiting_ai_response = False
        st.rerun()


users = api_get(f"/users/{CURRENT_USER_ID}") or {}

chat_options = [AI_CHAT_NAME]
chat_options.extend(users.values())
chat_options.append(EVENTS_SECTION)
chat_options.append(SMART_REVIEW_SECTION)

selected = st.sidebar.selectbox(
    "Workspace",
    chat_options,
    index=chat_options.index(st.session_state.selected_chat)
)

st.session_state.selected_chat = selected


st.markdown(
    """
    <div style="
        background:#0f172a;
        color:white;
        padding:22px 28px;
        border-radius:18px;
        margin-bottom:22px;
    ">
        <div style="font-size:26px;font-weight:700;">
            🤖 TeamSync
        </div>
        <div style="margin-top:6px;font-size:15px;color:#cbd5f5;">
            Your unified AI assistant for reviews, chat, analytics, documents, and internal intelligence
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


if selected == EVENTS_SECTION:
    st.markdown("## 📅 Event Dashboard")
    events = api_get("/events") or []

    for evt in events:
        status_color = "#22c55e" if evt["status"] == "completed" else "#f97316"

        st.markdown(
            f"""
            <div style="
                background:#f8fafc;
                border-radius:14px;
                padding:18px;
                margin-bottom:12px;
                border-left:6px solid {status_color};
            ">
                <div style="font-size:18px;font-weight:600;">
                    {evt['event']}
                </div>
                <div style="margin-top:6px;color:#475569;">
                    👥 {", ".join(evt['entities'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.stop()


if selected == SMART_REVIEW_SECTION:
    st.markdown("## 📝 Smart Review Analysis")

    review_text = st.text_area(
        "Paste review",
        height=220,
        placeholder="Paste any product, service, or customer review here..."
    )

    if st.button("🔍 Analyze Review") and review_text.strip():
        with st.spinner("TeamSync Agent is analyzing..."):
            res = api_post(
                "/ai/smart-review",
                {
                    "user_id": CURRENT_USER_ID,
                    "message": review_text
                }
            )

        if res and "response" in res:
            st.markdown("### 🤖 AI Response")
            st.markdown(
                f"""
                <div style="
                    background:#f1f5f9;
                    padding:18px;
                    border-radius:14px;
                    font-size:17px;
                    line-height:1.6;
                ">
                    {res['response']}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.error("Failed to get AI response")

    st.stop()


is_ai = selected == AI_CHAT_NAME
target_user_id = AI_USER_ID if is_ai else api_get(f"/users/id/{selected}")["user_id"]

history = [] if is_ai else api_get(
    f"/messages/history/{CURRENT_USER_ID}/{target_user_id}"
) or []

all_messages = history + st.session_state.temp_messages

st.markdown("<div style='padding-bottom:90px;'>", unsafe_allow_html=True)

for msg in all_messages:
    is_me = msg["sender_user_id"] == CURRENT_USER_ID
    bg = "#DCF8C6" if is_me else "#E5EDFF"
    align = "flex-end" if is_me else "flex-start"

    st.markdown(
        f"""
        <div style="display:flex;justify-content:{align};">
            <div style="
                background:{bg};
                padding:14px 18px;
                border-radius:14px;
                max-width:70%;
                margin:6px 0;
                font-size:18px;
            ">
                {msg["content"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)


user_input = st.chat_input(f"Message {selected}")

if user_input and not st.session_state.awaiting_ai_response:
    st.session_state.temp_messages.append(
        {"sender_user_id": CURRENT_USER_ID, "content": user_input}
    )

    if is_ai:
        st.session_state.pending_ai_message = user_input
        st.session_state.awaiting_ai_response = True

    st.rerun()


if st.session_state.awaiting_ai_response and st.session_state.pending_ai_message:
    with st.spinner("TeamSync Agent is thinking..."):
        res = api_post("/chat", {"message": st.session_state.pending_ai_message})

    if res and "response" in res:
        st.session_state.temp_messages.append(
            {"sender_user_id": AI_USER_ID, "content": res["response"]}
        )

    st.session_state.pending_ai_message = None
    st.session_state.awaiting_ai_response = False
    st.rerun()
