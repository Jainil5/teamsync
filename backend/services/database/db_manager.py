from pymongo import MongoClient, ASCENDING
from datetime import datetime
from uuid import uuid4
import certifi

from services.database.creds import URL
from services.database.translate_func import translate_text

# ================= CONFIG =================
DB_NAME = "TEAMSYNC-DB"
USERS_COL = "USERS"
MESSAGES_COL = "MESSAGES"
DEFAULT_LANGUAGE = "english"

# ================= MONGO CLIENT =================
client = MongoClient(
    URL,
    tls=True,
    tlsCAFile=certifi.where(),
    maxPoolSize=50,
    retryWrites=True
)

db = client[DB_NAME]
users_db = db[USERS_COL]
messages_db = db[MESSAGES_COL]

# ================= INDEXES =================
users_db.create_index("user_id", unique=True)
users_db.create_index("username", unique=True)

messages_db.create_index(
    [
        ("sender_user_id", ASCENDING),
        ("receiver_user_id", ASCENDING),
        ("created_at", ASCENDING),
    ]
)

# ================= USERS =================
def get_other_users_data(user_id: str) -> dict:
    cursor = users_db.find(
        {"user_id": {"$ne": user_id}},
        {"_id": 0, "user_id": 1, "username": 1}
    )
    return {doc["user_id"]: doc["username"] for doc in cursor}


def get_user_name(user_id: str) -> str | None:
    doc = users_db.find_one(
        {"user_id": user_id},
        {"_id": 0, "username": 1}
    )
    return doc["username"] if doc else None


def get_user_id(username: str) -> str | None:
    doc = users_db.find_one(
        {"username": username},
        {"_id": 0, "user_id": 1}
    )
    return doc["user_id"] if doc else None


def get_job_role(user_id: str) -> str | None:
    doc = users_db.find_one(
        {"user_id": user_id},
        {"_id": 0, "role": 1}
    )
    if not doc or "role" not in doc:
        return None
    return " | ".join(doc["role"]).upper()


def get_language(user_id: str) -> str:
    doc = users_db.find_one(
        {"user_id": user_id},
        {"_id": 0, "primary_language": 1}
    )
    return doc.get("primary_language", DEFAULT_LANGUAGE) if doc else DEFAULT_LANGUAGE


def get_chat_history(viewer_id: str, other_user_id: str) -> list:
    """
    Fetch chat history and adapt message content
    based on the viewer's primary language.
    """

    viewer_lang = get_language(viewer_id)

    messages = list(
        messages_db.find(
            {
                "$or": [
                    {"sender_user_id": viewer_id, "receiver_user_id": other_user_id},
                    {"sender_user_id": other_user_id, "receiver_user_id": viewer_id},
                ]
            },
            {"_id": 0}
        ).sort("created_at", ASCENDING)
    )

    for msg in messages:
        sender_id = msg["sender_user_id"]

        # Viewer should always see their own messages as-is
        if sender_id == viewer_id:
            msg.pop("translated", None)
            continue

        # Message sent by the other user
        sender_lang = get_language(sender_id)

        # Translate ONLY if viewer language != sender language
        if sender_lang != viewer_lang and msg.get("translated"):
            msg["content"] = msg["translated"]

        # Never expose translated field to frontend
        msg.pop("translated", None)

    return messages



def add_message(
    sender_id: str,
    receiver_id: str,
    content: str,
    team_id: int = 0
) -> None:
    sender_lang = get_language(sender_id)
    receiver_lang = get_language(receiver_id)

    translated = ""
    if sender_lang != receiver_lang:
        translated = translate_text(content, sender_lang, receiver_lang)

    now = datetime.utcnow()

    message = {
        "message_id": f"msg_{uuid4().hex}",
        "sender_user_id": sender_id,
        "receiver_user_id": receiver_id,
        "team_id": team_id,
        "content": content.strip(),
        "translated": translated.strip(),
        "created_at": now,  
    }

    messages_db.insert_one(message)
