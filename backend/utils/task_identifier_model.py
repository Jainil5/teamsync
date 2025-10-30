import requests
import json
from typing import Dict, List

# --- Configuration ---
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:1b"

# -------------------------------
# 1. Few-Shot Examples and Prompt Components
# -------------------------------
few_shot_examples: List[Dict[str, str]] = [
    {"message": "Let's connect tomorrow at 8 PM.", "task": "Connect with <PERSON> tomorrow at 8 PM."},
    {"message": "Send me the updates on project by Thursday.", "task": "Send project updates to <PERSON> by Thursday."},
    {"message": "Can you follow up with the backend team?", "task": "Follow up with backend team <PERSON>."},
    {"message": "Schedule a call with the manager.", "task": "Schedule call with <PERSON>."},
    {"message": "Remind me to review the code by evening.", "task": "Remind <PERSON> to review code by evening."},
    {"message": "Update client on this.", "task": "Update client."},
    {"message": "Let's plan the meeting tomorrow.", "task": "Plan meeting with <PERSON> tomorrow."},
    {"message": "Ask John for the latest report.", "task": "Ask John for latest report."},
    {"message": "We should discuss this next week.", "task": ""},
    {"message": "No issues here, everything is fine.", "task": ""},
    {"message": "Hey, what’s the progress on this?", "task": ""},
    {"message": "Let’s finalize the draft today.", "task": "Finalize draft with <PERSON> today."},
    {"message": "Follow up on shipment status.", "task": ""},
    {"message": "Ping the client for approval.", "task": ""},
    {"message": "No tasks today.", "task": ""},
    
    
]

EXAMPLE_TEMPLATE = "message: {message}\ntask: {task}"
EXAMPLE_SEPARATOR = "\n\n"

# The original prefix and suffix logic is now handled in the main function

def build_prompt(user_input: str) -> str:
    """Constructs the full few-shot prompt string."""
    
    # 1. Define Prefix
    prefix = "You are a event detector from conversation message. Extract the task or event from the user's message. Understand the message and identify any event or task from that. Output only the task string in a single line. Don't keep context of previous messages. Just task detection from this message. If there is no task, leave it empty. And use <PERSON> as a placeholder for any person which will be replaced later. But make sure to keep that tag. Providing you some examples as part of few shot learning. Generate answers accordingly.\n\n"
    
    # 2. Add Examples
    examples_str = EXAMPLE_SEPARATOR.join(
        EXAMPLE_TEMPLATE.format(message=ex["message"], task=ex["task"])
        for ex in few_shot_examples
    )
    
    # 3. Define Suffix for the new input
    suffix = f"message: {user_input}\ntask:"
    
    return prefix + examples_str + EXAMPLE_SEPARATOR + suffix


def detect_task(message: str) -> str:
    """Sends the formatted prompt directly to the Ollama API."""
    full_prompt = build_prompt(message)
    
    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False,  # We want a single, complete response
        "options": {
            "temperature": 0.0,
            # Max tokens is useful to ensure the model doesn't generate too much extra content
            "num_predict": 100 
        }
    }
    
    try:
        # Make the synchronous POST request
        response = requests.post(
            OLLAMA_API_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30 # Set a reasonable timeout
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Ollama returns a JSON response, we extract the 'response' field
        result = response.json()
        output = result.get("response", "").strip()

        # Clean output
        return output.replace("\n", " ").strip()

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama API: {e}")
        print("Please ensure the Ollama server is running and the model is pulled.")
        return f"ERROR: Could not connect to LLM."


if __name__ == "__main__":
    # Ensure you have 'requests' installed: pip install requests

    test_messages = [
        "Connect with Alex on Zoom tomorrow at 3 PM.",
        "Let's grab lunch next week.",
        "No tasks today.",
        "Submit the budget report by Wednesday.",
        "Can you share the backend updates?",
        "Remind me to call Sarah.",
        "Hey, how's it going?",
        "Schedule a meeting with the design team.",
        "Share the project files on mail."
    ]

    for msg in test_messages:
        result = detect_task(msg)
        print(f"Message: {msg}")
        print("Detected Task:", result)
        print("-" * 50)