from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.tools import tool
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.agents import create_agent
from langchain_core.prompts import MessagesPlaceholder
import os
import torch


TXT_PATH = "backend/services/team-documents/Project Alpha.txt"
CHROMA_DIR = "backend/models/chroma_db"


if torch.backends.mps.is_available():
    DEVICE = "mps"
elif torch.cuda.is_available():
    DEVICE = "cuda"
else:
    DEVICE = "cpu"

print(f"Using device: {DEVICE}")

OLLAMA_NUM_GPU = 1 if DEVICE == "cuda" else 0

embeddings = OllamaEmbeddings(
    model="nomic-embed-text:latest"
)


model = ChatOllama(
    model="gpt-oss:20b-cloud",
    temperature=0,
)

loader = TextLoader(TXT_PATH)
docs = loader.load()
print(f"Loaded document: {len(docs[0].page_content)} characters")

docs = str(docs).replace("\n", "")
docs = str(docs).replace("\t", "")
docs = str(docs).replace("*", "")
print(docs)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True
)
all_splits = text_splitter.split_documents(docs)
print(f"Split into {len(all_splits)} chunks")

vector_store = Chroma(
    collection_name="project_alpha",
    embedding_function=embeddings,
    persist_directory="backend/models/chroma_db"
)
document_ids = vector_store.add_documents(documents=all_splits)
print(f"Indexed {len(document_ids)} chunks. DB ready at ./chroma_db")


vector_store = Chroma(
    collection_name="project_alpha",
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR
)

if vector_store._collection.count() == 0:
    document_ids = vector_store.add_documents(all_splits)
    print(f"Indexed {len(document_ids)} chunks")
else:
    print("Using existing Chroma index")


@tool
def retrieve_context(query: str) -> str:
    """Retrieve relevant sections from Project Alpha documents to answer queries."""
    retrieved_docs = vector_store.similarity_search(query, k=3)
    return "\n\n---\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}..." 
        for doc in retrieved_docs
    )


tools = [retrieve_context]


system_prompt = """
You are a strict question-answering assistant.

Rules:
- Answer ONLY using the provided context.
- If the answer is not explicitly mentioned in the context, say:
  "The document does not contain this information."
- Do NOT use prior knowledge.
- Be concise and factual.
- Quote exact phrases when possible.
""".strip()


agent = create_agent(
    model,
    tools,
    system_prompt=system_prompt
)

def get_rag_response(query: str) -> str:
    try:
        response = agent.invoke(
            {"messages": [("user", query)]}
        )

        for msg in reversed(response["messages"]):
            if msg.type == "ai":
                return msg.content.strip()

        return "No clear answer generated."

    except Exception as e:
        return f"Error: {e}"


# if __name__ == "__main__":
#     while True:
#         user_input = input("Ask (or 'exit'): ").strip()
#         if user_input.lower() == "exit":
#             break

#         response = get_rag_response(user_input)
#         print(f"\nA: {response}\n")
