from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import json

llm = OllamaLLM(model="gemma3:1b")

prompt = ChatPromptTemplate.from_template("""
You are an assistant that extracts communication intent from messages.

Given a text command, identify:
1. All recipients mentioned.
2. The main action or message to be sent.

Return ONLY valid JSON in this format:

{{
  "recipients": ["name1", "name2"],
  "message": "text"
}}

Examples:
Input: "Ping David and frontend team to finalize the meeting agenda."
Output: {{"recipients": ["David", "frontend team"], "message": "Finalize the meeting agenda"}}

Input: "text to marketing team and Mann and David and HR team to finalize the proposal draft."
Output: {{"recipients": ["marketing team", "Mann", "David", "HR team"], "message": "Finalize the proposal draft"}}

Now extract recipients and message for:
"{message}"

JSON:
""")

test_messages = [
    "Text Riya to send me backend files.",
    "Ping Rina and HR team about the hiring update.",
    "Remind me to check the sales report tomorrow.",
    "Schedule a call with the marketing team next week.",
    "Send project launch details to Alex."
]

for msg in test_messages:
    formatted_prompt = prompt.format(message=msg)
    response = llm.invoke(formatted_prompt)
    response_text = response.strip()

    try:
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        cleaned_json = response_text[start:end]
        parsed = json.loads(cleaned_json)
    except Exception:
        parsed = {"raw_output": response_text}

    print(f"💬 Input: {msg}")
    print(f"➡️ Output: {json.dumps(parsed, indent=2)}")
    print("-" * 70)
