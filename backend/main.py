from fastapi import FastAPI
from pydantic import BaseModel

from services.main_agent import bot

from services.database.db_manager import (
    get_other_users_data,
    get_user_name,
    get_user_id,
    get_job_role,
    get_language,
    get_chat_history,
    add_message
)

app = FastAPI(
    title="TeamSync Backend",
    version="1.0.0"
)

AI_USER_ID = "teamsync_ai"

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str | dict | list


class SendMessageRequest(BaseModel):
    sender_id: str
    receiver_id: str
    content: str


class AIChatRequest(BaseModel):
    user_id: str
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Pure AI agent call (no DB)
    """
    return {"response": bot(req.message)}


@app.get("/users/{user_id}")
def users(user_id: str):
    return get_other_users_data(user_id)


@app.get("/users/name/{user_id}")
def user_name(user_id: str):
    return {"username": get_user_name(user_id)}


@app.get("/users/id/{username}")
def user_id(username: str):
    return {"user_id": get_user_id(username)}


@app.get("/users/role/{user_id}")
def user_role(user_id: str):
    return {"role": get_job_role(user_id)}


@app.get("/users/language/{user_id}")
def user_language(user_id: str):
    return {"language": get_language(user_id)}


@app.get("/messages/history/{user1}/{user2}")
def messages(user1: str, user2: str):
    return get_chat_history(user1, user2)


@app.post("/messages/send")
def send_message(req: SendMessageRequest):
    add_message(
        sender_id=req.sender_id,
        receiver_id=req.receiver_id,
        content=req.content
    )
    return {"status": "ok"}


@app.post("/ai/chat", response_model=ChatResponse)
def ai_chat(req: AIChatRequest):
    add_message(req.user_id, AI_USER_ID, req.message)

    ai_response = bot(req.message)

    add_message(AI_USER_ID, req.user_id, str(ai_response))

    return {"response": ai_response}



@app.post("/ai/smart-review", response_model=ChatResponse)
def ai_smart_review(req: AIChatRequest):
    add_message(req.user_id, AI_USER_ID, req.message)

    ai_response = bot(req.message)

    add_message(AI_USER_ID, req.user_id, str(ai_response))

    return {"response": ai_response}
