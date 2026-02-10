from bson import ObjectId
from pymongo import MongoClient
from utils.creds import URL
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

def add_user(user_data: dict):
    """Insert a new user document into users collection."""
    try:
        result = users_db.insert_one(user_data)
        print(f"✅ User added with ID: {result.inserted_id}")
    except Exception as e:
        print(f"❌ Error adding user: {e}")


def get_user_by_id(user_id: str):
    """Find user by ID."""
    try:
        user = users_db.find_one({"_id": ObjectId(user_id)})
        return user
    except Exception as e:
        print(f"❌ Error fetching user: {e}")


def get_all_users():
    """Return all users."""
    return list(users_db.find())


def update_user(user_id: str, update_data: dict):
    """Update specific fields of a user."""
    try:
        result = users_db.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )
        print(f"✅ {result.modified_count} user(s) updated")
    except Exception as e:
        print(f"❌ Error updating user: {e}")


def delete_user(user_id: str):
    """Delete user by ID."""
    try:
        result = users_db.delete_one({"_id": ObjectId(user_id)})
        print(f"🗑️ {result.deleted_count} user(s) deleted")
    except Exception as e:
        print(f"❌ Error deleting user: {e}")


# -----------------------------
# MESSAGE OPERATIONS
# -----------------------------
def add_message(message_data: dict):
    """Insert a new message."""
    try:
        result = messages_db.insert_one(message_data)
        print(f"💬 Message added with ID: {result.inserted_id}")
    except Exception as e:
        print(f"❌ Error adding message: {e}")


def get_messages_for_user(user_id: str):
    """Get all messages sent by a specific user."""
    try:
        messages = list(messages_db.find({"sender_id": user_id}))
        return messages
    except Exception as e:
        print(f"❌ Error fetching messages: {e}")


def delete_message(message_id: str):
    """Delete a message by ID."""
    try:
        result = messages_db.delete_one({"_id": ObjectId(message_id)})
        print(f"🗑️ {result.deleted_count} message(s) deleted")
    except Exception as e:
        print(f"❌ Error deleting message: {e}")


# -----------------------------
# DEMO USAGE
# -----------------------------
if __name__ == "__main__":
    # Add sample user
    add_user({"name": "Alice", "email": "alice@example.com"})

    # Fetch all users
    users = get_all_users()
    print("\n👥 All Users:")
    for u in users:
        print(u)

    # Add a message for the first user
    if users:
        user_id = str(users[0]["_id"])
        add_message({"sender_id": user_id, "text": "Hello from Alice!"})

    # Get all messages for a user
    messages = get_messages_for_user(user_id)
    print("\n💬 Messages by Alice:")
    for m in messages:
        print(m)