from pymongo import MongoClient
from frontend.creds import URL
import certifi

mongo_uri = URL
database_name = "TEAMSYNC"
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



# for doc in users_db.find():
#     print(doc)
# for doc in messages_db.find():
#     print(doc)    

# for doc in messages_db.find({"sender_user_id": "user_1", "receiver_user_id": "user_4"} or {"sender_user_id": "user_4", "receiver_user_id": "user_1"} ):    
#     print(doc["sender_user_id"],"---",doc["content"])

# new_user = "10"
# collection = main_db["10"]

# # 4. Insert a document (this also creates the collection if it doesn’t exist yet)
# doc = {"to": "user_2", "content": "Hello!", "city": "New York"}
# collection.insert_one(doc)    