import torch
import pandas as pd
from datasets import Dataset
from sklearn.preprocessing import LabelEncoder
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
)
import evaluate
import numpy as np
import joblib
import os

# ============================================================
# 1️⃣ Check for GPU
# ============================================================

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🧠 Using device: {device.upper()}")

# ============================================================
# 2️⃣ Load and prepare your dataset
# ============================================================

# Change the path to your dataset file
df = pd.read_csv("intent_dataset.csv")

# Encode labels (e.g., event, reminder, no_event)
le = LabelEncoder()
df["label"] = le.fit_transform(df["intent"])

# Convert to Hugging Face Dataset
dataset = Dataset.from_pandas(df[["message", "label"]])
dataset = dataset.train_test_split(test_size=0.2, seed=42)

# ============================================================
# 3️⃣ Tokenization
# ============================================================

model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def preprocess_function(examples):
    return tokenizer(examples["message"], truncation=True, padding="max_length", max_length=64)

tokenized_datasets = dataset.map(preprocess_function, batched=True)

# ============================================================
# 4️⃣ Load Model (on GPU if available)
# ============================================================

num_labels = len(le.classes_)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels).to(device)

# ============================================================
# 5️⃣ Define Metrics
# ============================================================

accuracy = evaluate.load("accuracy")
f1 = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    acc = accuracy.compute(predictions=predictions, references=labels)
    f1_score = f1.compute(predictions=predictions, references=labels, average="weighted")
    return {"accuracy": acc["accuracy"], "f1": f1_score["f1"]}

# ============================================================
# 6️⃣ Training Configuration
# ============================================================

training_args = TrainingArguments(
    output_dir="./intent_model_results",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=20,
    weight_decay=0.01,
    logging_dir="./logs",
    push_to_hub=False,
)

# ============================================================
# 7️⃣ Train the Model
# ============================================================

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

trainer.train()

# ============================================================
# 8️⃣ Evaluate and Save
# ============================================================

metrics = trainer.evaluate()
print(f"✅ Evaluation Results: {metrics}")

# Create directory for saving
save_dir = "./intent_model"
os.makedirs(save_dir, exist_ok=True)

# Save model, tokenizer, and label encoder
trainer.save_model(save_dir)
tokenizer.save_pretrained(save_dir)
joblib.dump(le, os.path.join(save_dir, "label_encoder.pkl"))

print(f"✅ Model, tokenizer, and label encoder saved in: {save_dir}")
print("Files include: pytorch_model.bin, config.json, tokenizer.json, vocab.txt, label_encoder.pkl")

# ============================================================
# 9️⃣ Quick Inference Test
# ============================================================

# 