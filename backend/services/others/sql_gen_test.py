import json
from sql_gen import sql_query_generator


SALES_CSV = "backend/services/team-documents/clothing_sales_combined.csv"
HEALTH_CSV = "backend/services/team-documents/healthcare_dataset.csv"

OUTPUT_JSON = "backend/services/sql_generation_test_results.json"


sales_questions = [
    "Find names of customers who bought Sneakers.",
    "List customer emails who paid using CASH.",
    "Get total revenue for customers who used CARD.",
    "Find customers who received any discount.",
    "Show average revenue by category.",
    "List products that were returned.",
    "Find customers aged more than 40.",
    "Get total discount amount for the month of October.",
    "Find customer IDs who bought products of size M.",
    "Show total revenue for the year 2024."
]


health_questions = [
    "Find patients with blood type A+.",
    "List names of patients admitted under Emergency.",
    "Get total billing amount for each insurance provider.",
    "Find patients older than 60.",
    "Show average billing amount for female patients.",
    "List patients treated by Matthew Smith.",
    "Find patients admitted in room numbers greater than 300.",
    "Show patients with Normal test results.",
    "Get total billing amount for Emergency admissions.",
    "List patients discharged after 2022."
]


results = {
    "sales": [],
    "healthcare": []
}


# ---------------- SALES ----------------
for q in sales_questions:
    sql = sql_query_generator(
        user_input=q,
        csv_path=SALES_CSV,
        table_name="Sales"
    )

    results["sales"].append({
        "question": q,
        "generated_sql": sql
    })


# ---------------- HEALTHCARE ----------------
for q in health_questions:
    sql = sql_query_generator(
        user_input=q,
        csv_path=HEALTH_CSV,
        table_name="Health"
    )

    results["healthcare"].append({
        "question": q,
        "generated_sql": sql
    })


# ---------------- SAVE JSON ----------------
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)


print(f"Saved SQL generation test results to {OUTPUT_JSON}")
