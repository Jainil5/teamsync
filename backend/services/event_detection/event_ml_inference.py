import joblib
import numpy as np

MODEL_DIR = "services/event_detection/models/"

vectorizer = joblib.load(MODEL_DIR + "tfidf_vectorizer.pkl")
label_encoder = joblib.load(MODEL_DIR + "label_encoder.pkl")
model = joblib.load(MODEL_DIR + "intent_classifier_lr.pkl")

def predict_intent(message: str) -> str:
    if not message or not message.strip():
        return "NO_INTENT"

    text = message.strip().lower()
    X_vec = vectorizer.transform([text])
    pred_encoded = model.predict(X_vec)[0]
    return str(label_encoder.inverse_transform([pred_encoded])[0])

# if __name__ == "__main__":
#     test_messages = [
#         "standup at 10am",
#         "remind me to deploy after lunch",
#         "fix the prod bug",
#         "lol that was funny",
#         "set a reminder for client call",
#         "townhall next week",
#         "thanks"
#     ]

#     for msg in test_messages:
#         print(msg, "->", predict_intent(msg))

# print(predict_intent("We need to meet today evening."))
