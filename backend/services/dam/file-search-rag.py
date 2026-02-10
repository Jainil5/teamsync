
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from tqdm import tqdm

df = pd.read_csv("backend/utils/dam/file_descriptions.csv")
print(f"Loaded {len(df)} file descriptions.")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_store")

collection = chroma_client.get_or_create_collection(
    name="file_descriptions",
    embedding_function=None
)

if collection.count() == 0:
    print("Adding file descriptions to ChromaDB...")

    descriptions = df["description"].tolist()
    ids = [str(i) for i in df["file_id"].tolist()]
    metadatas = [{"file_name": f} for f in df["file_name"].tolist()]

    print("Generating embeddings in batches...")
    embeddings = embedding_model.encode(
        descriptions, batch_size=16, show_progress_bar=True
    )

    print("Storing vectors in ChromaDB...")
    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=descriptions,
        metadatas=metadatas
    )

    print(f"? Added {collection.count()} records to ChromaDB.")
else:
    print(f"? Found existing ChromaDB with {collection.count()} records.")

def search_files(query, top_k=3):
    query_emb = embedding_model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_emb], n_results=top_k)

    if not results or not results["documents"][0]:
        print("No matches found.")
        return pd.DataFrame(columns=["file_name", "description", "similarity_score"])

    hits = []
    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        hits.append({
            "file_name": meta.get("file_name", "Unknown"),
            "description": doc,
            "similarity_score": distance
        })

    return pd.DataFrame(hits)

if __name__ == "__main__":
    print("\nAI File Search System Ready!")
    print("Type your query (or 'exit' to quit)\n")

    while True:
        user_query = input("Enter your query: ").strip()
        if user_query.lower() in ["exit", "quit"]:
            print("Exiting.")
            break

        df_results = search_files(user_query, top_k=3)
        if df_results.empty:
            print("No relevant files found.\n")
        else:
            print("\nTop File Suggestions:")
            for x,y in df_results.iterrows():
                print(x,y)
            print("\n" + "-" * 80 + "\n")
