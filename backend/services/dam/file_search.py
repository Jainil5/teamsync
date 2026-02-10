import os
import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "file_descriptions.csv")

df = pd.read_csv(CSV_PATH)

REQUIRED_COLUMNS = {"file_name", "link", "description"}
missing = REQUIRED_COLUMNS - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {missing}")



def parse_description(desc: str) -> dict:
    try:
        return json.loads(desc)
    except Exception:
        return {}


def build_search_text(desc_json: dict) -> str:
    title = desc_json.get("title", "")
    caption = desc_json.get("caption", "")
    keywords = " ".join(desc_json.get("keywords", []))

    return f"{title} {caption} {keywords}".strip()


df["desc_json"] = df["description"].apply(parse_description)

df["search_text"] = df["desc_json"].apply(build_search_text)
df["caption"] = df["desc_json"].apply(lambda x: x.get("caption", ""))


vectorizer = TfidfVectorizer(
    stop_words="english",
    max_df=0.9,
    min_df=1
)

tfidf_matrix = vectorizer.fit_transform(df["search_text"])


def rank_files(query: str, top_k: int):
    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

    if similarities.max() == 0:
        return None

    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return top_indices, similarities


def format_as_text(results_df: pd.DataFrame, query: str) -> str:
    lines = [
        f"I found the following documents related to: '{query}'\n"
    ]

    for i, row in results_df.iterrows():
        lines.append(
            f"File Name : {row['file_name']}\n"
            f"\nSummary(AI-generated)   : {row['caption']}\n"
            # f"   Relevance : {row['score']}\n"
            f"\nLink      : {row['link'] or 'Not available'}\n"
        )

    return "\n".join(lines)

def search_files(
    query: str,
    top_k: int = 3,
    return_format: str = "text"
):

    ranked = rank_files(query, top_k)
    if not ranked:
        return "No relevant documents were found for your query."

    top_indices, similarities = ranked

    results = df.iloc[top_indices][
        ["file_name", "link", "caption"]
    ].copy()

    results["score"] = similarities[top_indices].round(3)

    if return_format == "df":
        return results.reset_index(drop=True)

    if return_format == "json":
        return results.to_dict(orient="records")

    return format_as_text(results, query)




print(search_files("Find me document that mentions leave policy")) 