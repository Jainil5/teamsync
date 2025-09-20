from flask import Flask, request, jsonify, Response, render_template
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import json
import time
from frontend.creds import URL # Assuming creds.py contains the MongoDB URL
import certifi

app = Flask(__name__)

# -------------------------------
# MongoDB Setup
# -------------------------------
mongo_uri = URL
database_name = "TEAMSYNC"
collection_users = "USERS"
collection_messages = "MESSAGES"
# Note: For the tailable cursor in stream(), the MESSAGES collection must be a capped collection.
# To create it from the Mongo shell:
# db.createCollection("MESSAGES", { capped: true, size: 1000000 }) # 1MB capped collection

try:
    client = MongoClient(mongo_uri,
        client.admin.command("ping")
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
    )
main_db = client[database_name]
users_db = main_db[collection_users]
messages_db = main_db[collection_messages]


# -------------------------------
# Login API
# -------------------------------
@app.route("/api/login", methods=["POST"])
def login():
    """Authenticates a user and returns their details."""
    data = request.json
    user_id = data.get("user_id")
    password = data.get("password")

    user = users_db.find_one({"user_id": user_id, "password": password})
    if not user:
        return jsonify({"ok": False, "error": "Invalid credentials"}), 401

    # Remove the password and convert ObjectId to string before sending
    user.pop("password", None)
    user["_id"] = str(user["_id"])
    return jsonify({"ok": True, "user": user})


# -------------------------------
# Get all users
# -------------------------------
@app.route("/api/users", methods=["GET"])
def get_users():
    """Returns a list of all users."""
    users = list(users_db.find({}, {"_id": 1, "user_id": 1, "username": 1, "profile_picture_url": 1}))
    for u in users:
        u["_id"] = str(u["_id"])
    return jsonify(users)


# -------------------------------
# Get all messages for a team
# -------------------------------
@app.route("/api/messages", methods=["GET"])
def get_messages():
    """Returns messages for a specific team (channel)."""
    team_id = int(request.args.get("team_id", 0))
    msgs = list(messages_db.find({"team_id": team_id}).sort("timestamp", 1))
    for m in msgs:
        m["_id"] = str(m["_id"])
    return jsonify(msgs)


# -------------------------------
# Get direct messages between two users
# -------------------------------
@app.route("/api/direct_messages", methods=["GET"])
def get_direct_messages():
    """Returns direct messages between two users."""
    user_id = request.args.get("user_id")
    recipient_id = request.args.get("recipient_id")

    # Find messages where the sender and receiver are the two users
    query = {
        "$or": [
            {"$and": [{"sender_user_id": user_id}, {"recipient_user_id": recipient_id}]},
            {"$and": [{"sender_user_id": recipient_id}, {"recipient_user_id": user_id}]}
        ]
    }
    
    msgs = list(messages_db.find(query).sort("timestamp", 1))
    for m in msgs:
        m["_id"] = str(m["_id"])
    return jsonify(msgs)


# -------------------------------
# Send message to a team
# -------------------------------
@app.route("/api/send", methods=["POST"])
def send_message():
    """Sends a message to a team (channel)."""
    data = request.json
    sender_user_id = data.get("sender_user_id")
    team_id = int(data.get("team_id", 0))
    content = data.get("content")

    msg = {
        "sender_user_id": sender_user_id,
        "team_id": team_id,
        "content": content,
        "timestamp": datetime.utcnow(),
    }
    messages_db.insert_one(msg)
    return jsonify({"ok": True})


# -------------------------------
# Send a direct message
# -------------------------------
@app.route("/api/send_direct", methods=["POST"])
def send_direct_message():
    """Sends a direct message to a specific user."""
    data = request.json
    sender_user_id = data.get("sender_user_id")
    recipient_user_id = data.get("recipient_user_id")
    content = data.get("content")

    msg = {
        "sender_user_id": sender_user_id,
        "recipient_user_id": recipient_user_id,
        "content": content,
        "timestamp": datetime.utcnow(),
    }
    messages_db.insert_one(msg)
    return jsonify({"ok": True})


# -------------------------------
# Real-time Streaming (SSE)
# -------------------------------
@app.route("/api/stream")
def stream():
    """
    Streams new messages to the client using Server-Sent Events (SSE).
    Uses a tailable cursor on a capped collection for efficient real-time updates.
    """
    def event_stream():
        # The tailable cursor will wait for new data if it reaches the end of the collection
        cursor = messages_db.find(
            {"team_id": 0},  # Filter for the main team chat
            cursor_type=4,  # Use Tailable Cursor (4)
            await_data=True,
            oplog_replay=True # Tailable cursor settings
        )
        
        while cursor.alive:
            try:
                msg = cursor.next()
                msg["_id"] = str(msg["_id"])
                msg["time"] = msg["timestamp"].strftime("%H:%M")
                msg.pop("timestamp") # Clean up timestamp field
                
                # Yield the new message
                yield f"data: {json.dumps({'type':'message','data':msg})}\n\n"
            except StopIteration:
                # No new data yet, wait for a bit
                time.sleep(0.1)

    return Response(event_stream(), mimetype="text/event-stream")


# -------------------------------
# Serve HTML pages
# -------------------------------
@app.route("/")
def home():
    """Renders the login page."""
    return render_template("chat.html")

# -------------------------------
# Run server
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)