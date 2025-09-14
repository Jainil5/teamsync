from pymongo import MongoClient

    # ----------------------------------------------------------------------------
    # IMPORTANT: Replace the placeholder values with your actual data.
    # ----------------------------------------------------------------------------
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

# for doc in users_db.find():
#     print(doc)
# for doc in messages_db.find():
#     print(doc)    

messages = messages_db.find_one({"sender_user_id":"user_1","receiver_user_id":"user_2"})

print(messages)