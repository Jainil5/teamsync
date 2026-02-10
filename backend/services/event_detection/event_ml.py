import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

DATASET_PATH = "backend/services/event_detection/communication_intent_dataset_10k.csv"
MODEL_DIR = "backend/services/event_detection/models/"

df = pd.read_csv(DATASET_PATH)

df["message"] = df["message"].astype(str).str.strip().str.lower()
df["label"] = df["label"].astype(str).str.strip()

X = df["message"]

label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df["label"])

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

vectorizer = TfidfVectorizer(
    lowercase=True,
    min_df=3,
    max_df=0.9,
    sublinear_tf=True
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

model = LogisticRegression(
    max_iter=4000,
    class_weight="balanced",
    n_jobs=-1
)

model.fit(X_train_vec, y_train)

y_pred = model.predict(X_test_vec)

metrics = {
    "accuracy": accuracy_score(y_test, y_pred),
    "precision_macro": precision_score(y_test, y_pred, average="macro"),
    "recall_macro": recall_score(y_test, y_pred, average="macro"),
    "f1_macro": f1_score(y_test, y_pred, average="macro"),
    "precision_weighted": precision_score(y_test, y_pred, average="weighted"),
    "recall_weighted": recall_score(y_test, y_pred, average="weighted"),
    "f1_weighted": f1_score(y_test, y_pred, average="weighted")
}

print(metrics)
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

joblib.dump(vectorizer, MODEL_DIR + "tfidf_vectorizer.pkl")
joblib.dump(label_encoder, MODEL_DIR + "label_encoder.pkl")
joblib.dump(model, MODEL_DIR + "intent_classifier_lr.pkl")

pd.DataFrame([metrics]).to_csv(MODEL_DIR + "training_metrics.csv", index=False)
