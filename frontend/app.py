import streamlit as st
from db_manager import get_users_data, get_user_name, get_chat_history, get_user_id, add_message
from streamlit_autorefresh import st_autorefresh  

# -------------------
# Config & Variables
# -------------------
user_id = "user_1"
user_name = get_user_name(user_id)
job_role = "Software Developer"

st.set_page_config(
    page_title=f"{user_name}'s TeamSync",
    page_icon=":speech_balloon:",
    layout="wide"
)

# -------------------
# Sidebar Navigation
# -------------------
if "selected_chat" not in st.session_state:
    st.session_state["selected_chat"] = "HOME"

st_autorefresh(interval=10_000, key="refresh_chat")

welcome_text = f"Hello, {user_name} !"
user_list = get_users_data(user_id)

main_list = ["HOME"]
main_list.extend(user_list.values())

st.sidebar.title(welcome_text)
st.sidebar.divider()

to = st.sidebar.selectbox(
    "Direct Messages:", 
    options=main_list, 
    index=main_list.index(st.session_state["selected_chat"])
)

st.session_state["selected_chat"] = to

# -------------------
# Home Page
# -------------------
if to == "HOME":
    st.markdown(
        f"<div style='padding:20px; font-family:Segoe UI, sans-serif;'>"
        f"<h1 style='margin:0;'>{welcome_text}</h1>"
        f"<h3 style='margin-top:10px;'>Welcome to TeamSync, your AI-powered collaborative workspace!</h3>"
        f"</div>", 
        unsafe_allow_html=True
    )

# -------------------
# Chat Page
# -------------------
else:
    # Header / About user section (fixed)
    st.markdown(
        f"""
        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            padding:15px 20px;
            background:black;
            border-bottom:1px solid #ddd;
            position:sticky;
            top:0;
            z-index:999;
            box-shadow:0 4px 12px rgba(0,0,0,0.08);
            font-family:Segoe UI, sans-serif;
        ">
            <div style='display:flex; align-items:center; gap:15px;'>
                <img src='https://cdn-icons-png.flaticon.com/512/149/149071.png' style='border-radius:50%; width:60px; height:60px;'/>
                <h3 style='margin:0; color:white;'>{to}</h3>
            </div>
            <h2 style='margin:0; color:white;'>{job_role}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    # # Chat container with scrollable messages
    # st.markdown("<div style='height:500px; overflow-y:auto; padding:20px; margin:15px; border:1px solid #ddd; border-radius:12px; background-color:#ffffff;'>", unsafe_allow_html=True)

    # Get chat history
    to_id = get_user_id(to)
    message_list = get_chat_history(user_id, to_id)
    
    for message in message_list:
        if message["content"] and message["content"].strip() != "":
            if message["sender_user_id"] == user_id:
                st.markdown(
                    f"<div style='padding:10px 14px; border-radius:12px; margin:5px 0; max-width:70%; word-wrap:break-word; white-space:pre-wrap; font-size:15px; color:black; background:#d4f7d4; margin-left:auto; text-align:right;'>{message['content']}</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<div style='padding:10px 14px; border-radius:12px; margin:5px 0; max-width:70%; word-wrap:break-word; white-space:pre-wrap; font-size:15px; color:black; background:#d4eaff; border:1px solid #ddd; margin-right:auto; text-align:left;'>{message['content']}</div>",
                    unsafe_allow_html=True
                )


    
    # Input field
    input_msg = st.chat_input(f"Enter Message for {str(user_name).upper()} - ( {str(job_role).upper()} )")
    if input_msg:
        add_message(user_id, to_id, input_msg)
        st.rerun()

    # st.markdown(
    #     f"""
    #     <div style="
    #         display:flex;
    #         justify-content:space-between;
    #         align-items:center;
    #         padding:10px 10px;
    #         background:black;
    #         position:sticky;
    #         box-shadow:0 4px 12px rgba(0,0,0,0.08);
    #         font-family:Segoe UI, sans-serif;
    #     ">
    #         <div style='display:flex; align-items:center; gap:15px;'>
    #             <img src='https://cdn-icons-png.flaticon.com/512/149/149071.png' style='border-radius:50%; width:60px; height:60px;'/>
    #             <h2 style='margin:0; color:white;'>{to}</h2>
    #         </div>
    #         <h2 style='margin:0; color:white;'>{job_role}</h2>
    #     </div>
    #     """,
    #     unsafe_allow_html=True
    # )