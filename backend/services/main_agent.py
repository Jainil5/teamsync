from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain.tools import tool
import requests

from .others.sql_gen import sql_query_generator
from .others.rag_leave import get_rag_response
# from others.rag_project_alpha import leave_query_rag
from .event_detection.event_ml_inference import predict_intent
from .dam.file_search import search_files


# -------------------- LLM --------------------
llm = ChatOllama(
    model="gpt-oss:20b-cloud",
    temperature=0,
)


# -------------------- TOOLS --------------------
@tool
def get_weather(location: str):
    """Get the weather for a given location."""
    response = requests.get(f"https://wttr.in/{location}?format=j1")
    return response.json()


@tool
def generate_sql_sales(text: str):
    """Generate SQL query for the sales dataset."""
    columns, response = sql_query_generator(
        text,
        csv_path="services/team-documents/clothing_sales_combined.csv",
        table_name="Sales"
    )
    print("--------- SQL SALES TOOL CALLED ---------")
    return response


@tool
def generate_sql_health(text: str):
    """Generate SQL query for the healthcare dataset."""
    columns, response = sql_query_generator(
        text,
        csv_path="services/team-documents/healthcare_dataset.csv",
        table_name="Health"
    )
    print("--------- SQL HEALTH TOOL CALLED ---------")
    return response


@tool
def leave_policy(text: str):
    """Answer leave-policy-related questions using RAG."""
    return get_rag_response(text)


@tool
def file_search(text: str):
    """Search documents using DAM."""
    return search_files(text)


@tool
def predict_event(text: str):
    """Convert meeting, task, or reminder messages into structured intent."""
    return str(predict_intent(text)).lower() + " added."


@tool
def smart_review(text: str):
    """Generate a professional response to a customer review."""
    return str(generate_response(text)).lower() + " added."

# -------------------- AGENT PROMPT --------------------
agent_prompt = """
You are a STRICT tool-routing assistant.

ABSOLUTE RULES:
- Do NOT think out loud.
- Do NOT explain reasoning.
- Do NOT add text before or after tool output.
- Do NOT reformat, summarize, or interpret tool output.
- Do NOT mention tools or tool usage.

CORE BEHAVIOR:
- If a tool is called, return its output EXACTLY as received.
- Treat tool output as final and authoritative.
- If no tool applies, answer directly in plain text.

--------------------------------------------------
MANDATORY TOOL ROUTING
--------------------------------------------------

1. predict_event
- Meetings, scheduling, reminders, tasks, deadlines.

2. leave_policy
- Leave policy, HR rules, approvals, rejections, maternity/sick/casual leave.

3. file_search
- File search, document lookup, research papers.

4. generate_sql_sales
- Sales dataset questions only.

5. generate_sql_health
- Healthcare dataset questions only.

6. get_weather
- Weather-related questions only.
"""


# -------------------- AGENT --------------------
agent = create_agent(
    llm,
    tools=[
        get_weather,
        generate_sql_sales,
        generate_sql_health,
        leave_policy,
        file_search,
        predict_event
    ],
    system_prompt=agent_prompt
)


# -------------------- BOT FUNCTION --------------------
def bot(user_input: str):
    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]}
    )
    return response["messages"][-1].content


# ==================================================
# ===================== TESTING ====================
# ==================================================

# all_queries = [
#     # Event / Intent
#     "We need to meet today evening.",
#     "Remind me to submit the assignment tomorrow.",
#     "Schedule a follow-up call next week.",

#     # Leave / HR
#     "Why was my leave application rejected?",
#     "How many maternity leaves do I get?",
#     "What is the sick leave policy?",

#     # File Search
#     "Find me a file related to leave policy.",
#     "Find me research paper on h2ogpt.",

#     # Sales SQL
#     "Find total revenue for female customers who paid using CARD.",
#     "How average discount amount by category for products that were returned.",

#     # Health SQL
#     "Find patients older than 50 admitted under Emergency.",
#     "List patients admitted for diagnosis related to heart."
# ]

samples =     [
    "Find me a file related to leave policy.",
    "Find me research paper on h2ogpt.",
    "Why was my leave application rejected?",
    "How many maternity leaves do I get?",
    "Find patients older than 50 with blood group A+ admitted under Emergency.",
    "Find total revenue for female customers who paid using CARD.",

]

# # -------------------- RUN TESTS --------------------
# print("\n===== RUNNING ALL TEST QUERIES =====\n")

# for i, query in enumerate(all_queries, start=1):
#     print("--------------------------------------------------")
#     print(f"\n[{i}] Q: {query}")
#     print("A:", bot(query))
#     print("--------------------------------------------------")
