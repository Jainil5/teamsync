from pymongo import MongoClient
from datetime import datetime
import os
from .creds import URL
import certifi
from .translate_func import translate_text


mongo_uri = URL
database_name = "TEAMSYNC-DB"
collection_users = "USERS"
collection_messages = "MESSAGES"

try:
    client = MongoClient(mongo_uri,
       tls=True,
    tlsCAFile=certifi.where()
    )
    client.admin.command("ping")
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")

main_db = client[database_name]
users_db = main_db[collection_users]
messages_db = main_db[collection_messages]
users_col = users_db
messages_col = messages_db

# --------------------------------------
def get_other_users_data(user_id):
    """Fetch list of all users"""
    final = {}
    for doc in users_db.find():
        uid = doc["user_id"]
        name = doc["username"]
        if uid != user_id:    
            final.update({uid: name})
    return final

def get_user_name(user_id):
    for doc in users_db.find():
        uid = doc["user_id"]
        name = doc["username"]
        if uid == user_id:    
            return name  

def get_user_id(user_name):
    for doc in users_db.find():
        uid = doc["user_id"]
        name = doc["username"]
        if name == user_name:    
            return uid  

def get_job_role(user_id):
    for doc in users_db.find():
        uid = doc["user_id"]
        roles = doc["role"]
        if uid == user_id:    
            roles = str(roles)
            roles = roles.replace("[","")
            roles = roles.replace("]","")
            roles = roles.replace("'","")
            roles = roles.replace('"',"")
            roles = roles.replace(","," |")
            roles = str(roles).strip()
            roles = roles.upper()
            return roles


def get_chat_history(user1_id: str, user2_id: str):
    """Fetch chat history between two users"""
    chats = messages_db.find(
        {
            "$or": [
                {"sender_user_id": user1_id, "receiver_user_id": user2_id},
                {"sender_user_id": user2_id, "receiver_user_id": user1_id},
            ]
        },
        {"_id": 0}
    )
    sorted_data = sorted(
    chats.to_list(),
    key=lambda x: datetime.strptime(x['date'] + ' ' + x['time'], "%Y-%m-%d %H:%M:%S")
    )

    return list(sorted_data)

def get_language(user_id):
    for doc in users_db.find():
        uid = doc["user_id"]
        lang = doc["primary_language"]
        if uid == user_id:    
            return lang
        
def add_message(sender_id: str, receiver_id: str, content: str, team_id: int = 0):
    # Check if sender & receiver languages are the same
    if get_language(receiver_id) != get_language(sender_id):
    
        translated_content = translate_text(content, get_language(sender_id), get_language(receiver_id))
    else:
        translated_content = ""
    # Prepare message dictionary
    message = {
        "message_id": f"msg_{int(datetime.utcnow().timestamp())}",  # unique msg id
        "sender_user_id": sender_id,
        "receiver_user_id": receiver_id,
        "team_id": team_id,
        "content": str(content).strip(),
        "translated": str(translated_content).strip(),
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "time": datetime.utcnow().strftime("%H:%M:%S"),
    }

    # Insert into MongoDB
    messages_db.insert_one(message)
    


        


    
# print(add_message("user_1", "user_2", "Hello, Sir. I hope you are doing well."))          
# print(get_language("user_2"))          
# print(get_job_role("user_1"))        
# print(get_user_name("user_1"))
# print(get_user_id("Jainil Patel"))
# print(get_chat_history("user_5", "user_1"))
# for i in get_chat_history("user_5", "user_1"):
#     print(i["content"])






# -------------------------------
# USER MANAGEMENT
# -------------------------------
# def get_user_by_id(user_id: str):
#     """Fetch a single user by user_id"""
#     return users_col.find_one({"user_id": user_id}, {"_id": 0})

# MESSAGE MANAGEMENT
# -------------------------------
# def add_message(sender_id: str, receiver_id: str, content: str, team_id: int = 0, translated: str = ""):
#     """Insert a new message"""
#     message = {
#         "message_id": f"msg_{int(datetime.utcnow().timestamp())}",  # unique msg id
#         "sender_user_id": sender_id,
#         "receiver_user_id": receiver_id,
#         "team_id": team_id,
#         "content": content,
#         "translated": translated,
#         "date": datetime.utcnow().strftime("%Y-%m-%d"),
#         "time": datetime.utcnow().strftime("%H:%M:%S"),
#     }
#     messages_col.insert_one(message)
#     return message

# def get_chat_history(user1_id: str, user2_id: str):
#     """Fetch chat history between two users"""
#     chats = messages_db.find(
#         {
#             "$or": [
#                 {"sender_user_id": user1_id, "receiver_user_id": user2_id},
#                 {"sender_user_id": user2_id, "receiver_user_id": user1_id},
#             ]
#         },
#         {"_id": 0}
#     ).sort("date", 1).sort("time", 1)
#     return list(chats)

# def get_all_users():
#     """Fetch all users with only user_id and name"""
#     return list(users_col.find({}, {"_id": 0, "user_id": 1, "name": 1}))

