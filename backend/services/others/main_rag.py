import os

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama

from langchain_faiss import FAISS

from langchain.chains import RetrievalQA


# ==========================
# CONFIG
# ==========================

DATA_FOLDER = "data"
FAISS_INDEX_PATH = "faiss_index"

EMBED_MODEL = "nomic-embed-text"   # Ollama embedding model
LLM_MODEL = "llama3"               # Ollama LLM


# ==========================
# LOAD DOCUMENTS
# ==========================

def load_documents(folder):
    documents = []

    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)

        if filename.endswith(".pdf"):
            loader = PyPDFLoader(path)

        elif filename.endswith(".txt"):
            loader = TextLoader(path)

        elif filename.endswith(".docx"):
            loader = Docx2txtLoader(path)

        else:
            continue

        docs = loader.load()

        for d in docs:
            d.metadata["source_file"] = filename

        documents.extend(docs)

    return documents


print("📂 Loading documents...")
docs = load_documents(DATA_FOLDER)
print(f"Loaded {len(docs)} pages")


# ==========================
# CHUNK DOCUMENTS
# ==========================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)

chunks = splitter.split_documents(docs)

print(f"✂ Created {len(chunks)} chunks")


# ==========================
# OLLAMA EMBEDDINGS
# ==========================

embeddings = OllamaEmbeddings(
    model=EMBED_MODEL
)


# ==========================
# BUILD FAISS INDEX
# ==========================

print("📦 Building FAISS index...")

vectorstore = FAISS.from_documents(
    chunks,
    embeddings
)

vectorstore.save_local(FAISS_INDEX_PATH)

print("✅ FAISS index saved locally")


# ==========================
# LOAD INDEX
# ==========================

def load_faiss():
    return FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


# ==========================
# SEMANTIC FILE SEARCH
# ==========================

def semantic_file_search(query, k=5):
    db = load_faiss()

    results = db.similarity_search(query, k=k)

    print("\n🔍 SEMANTIC FILE SEARCH RESULTS\n")

    for r in results:
        print("📄 File:", r.metadata["source_file"])
        print("🧾 Snippet:", r.page_content[:200])
        print("-" * 60)


# ==========================
# OLLAMA LLM
# ==========================

llm = Ollama(
    model=LLM_MODEL,
    temperature=0
)


# ==========================
# RAG QA FUNCTION
# ==========================

def rag_query(question, k=5):
    db = load_faiss()

    retriever = db.as_retriever(
        search_kwargs={"k": k}
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    result = qa_chain(question)

    print("\n🤖 ANSWER:\n")
    print(result["result"])

    print("\n📚 SOURCES:\n")
    for doc in result["source_documents"]:
        print(doc.metadata["source_file"])


# ==========================
# TEST
# ==========================

if __name__ == "__main__":

    # 🔍 Semantic file search
    semantic_file_search("company leave policy")

    # 🤖 RAG question
    rag_query("What is the company leave policy?")
