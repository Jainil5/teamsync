from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import json

llm = OllamaLLM(model="gemma3:1b")

prompt = ChatPromptTemplate.from_template("""
You are an assistant that rewrites workplace chat messages into short, clean dashboard text.

Rules:
- Remove filler words (please, will, kindly, etc.)
- Remove unnecessary pronouns
- Do NOT invent new details
- Keep original meaning
- Keep output concise and professional
- Capitalize properly
- Max 8 words

Return ONLY valid JSON in this format:

{{
  "dashboard_text": "text"
}}

Examples:
Input: "We will have a Standup meeting at 10 am"
Output: {{"dashboard_text": "Standup meeting at 10 am"}}

Input: "Please share the backend file by monday."
Output: {{"dashboard_text": "Share the backend file by Monday"}}

Now rewrite this message:
"{message}"

JSON:
""")

def generate_dashboard_text(message: str) -> str:
    if not message or not message.strip():
        return ""

    formatted_prompt = prompt.format(message=message)
    response = llm.invoke(formatted_prompt).strip()

    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        cleaned_json = response[start:end]
        parsed = json.loads(cleaned_json)
        return parsed.get("dashboard_text", "")
    except Exception:
        return ""



print(generate_dashboard_text("We will have a Standup meeting at 10 am"))
print(generate_dashboard_text("Please share the backend file by monday."))
print(generate_dashboard_text("Kindly deploy the build after lunch."))
