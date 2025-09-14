# teamsync_streamlit_login.py
# Streamlit login page for project: teamsync with DB authentication

import streamlit as st
from pymongo import MongoClient
import hashlib

# -----------------------
# MongoDB CONNECTION
# -----------------------
mongo_uri = "mongodb+srv://jainiljp72525:messi%401010@users.9tdxb.mongodb.net/"
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

# -----------------------
# Streamlit Config
# -----------------------
st.set_page_config(page_title="teamsync — Login", page_icon="🔐", layout="centered")

# -----------------------
# Styling
# -----------------------
st.markdown("""
<style>
    .login-card {
        max-width: 480px;
        margin: 40px auto;
        padding: 28px;
        border-radius: 12px;
        box-shadow: 0 6px 24px rgba(32,33,36,0.08);
        background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(249,250,252,0.96));
    }
    .login-title {
        font-size: 34px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .login-subtitle {
        font-size: 13px;
        color: #6b7280;
        margin-bottom: 20px;
    }
    input[type="text"], input[type="password"], textarea {
        font-size: 18px !important;
        padding: 14px !important;
    }
    .stButton>button {
        padding: 12px 18px;
        font-size: 18px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------
# Login Form
# -----------------------
st.markdown('<div class="login-card">', unsafe_allow_html=True)
st.markdown('<div class="login-title">teamsync</div>', unsafe_allow_html=True)
st.markdown('<div class="login-subtitle">Welcome back — please sign in to continue</div>', unsafe_allow_html=True)

with st.form(key="login_form"):
    user_id = st.text_input("User ID", placeholder="Enter your user id", key="user_id")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="password")
    submitted = st.form_submit_button("Enter")

    if submitted:
        if not user_id.strip() or not password.strip():
            st.warning("Both User ID and Password are required — please fill in both fields.")
        else:
            print(users_db)
            user = users_db.find_one({"user_id": user_id, "password_hash": password})
            
            if user:
                st.session_state["user_id"] = user_id
                st.success(f"Welcome {user_id}, redirecting to dashboard...")

            else:
                st.error("Invalid User ID or Password.")

st.markdown('</div>', unsafe_allow_html=True)

