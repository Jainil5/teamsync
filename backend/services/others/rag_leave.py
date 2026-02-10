from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.tools import tool
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.agents import create_agent
from langchain_core.prompts import MessagesPlaceholder

PDF_PATH = "services/team-documents/Leave Policy.pdf"

embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

model = ChatOllama(
    model="gpt-oss:20b-cloud",
    temperature=0
)

loader = PyPDFLoader(PDF_PATH)
docs = loader.load()
# print(f"Loaded document: {len(docs[0].page_content)} characters")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True
)
all_splits = text_splitter.split_documents(docs)
# print(f"Split into {len(all_splits)} chunks")

vector_store = Chroma(
    collection_name="leave_policy",
    embedding_function=embeddings,
    persist_directory="backend/models/chroma_db"
)
document_ids = vector_store.add_documents(documents=all_splits)
# print(f"Indexed {len(document_ids)} chunks. DB ready at ./chroma_db")

@tool
def retrieve_context(query: str) -> str:
    """Retrieve relevant sections from Leave Policy documents to answer queries."""
    retrieved_docs = vector_store.similarity_search(query, k=3)
    return "\n\n---\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}..." 
        for doc in retrieved_docs
    )

tools = [retrieve_context]

system_prompt = (
    "You are a helpful assistant answering questions about Leave Policy. "
    "Use the retrieve_context tool to get relevant document sections. "
    "Base answers ONLY on retrieved context. If unsure, say so."
)

agent = create_agent(
    model, 
    tools, 
    system_prompt = system_prompt
)


def get_rag_response(query: str) -> str:
    """Run agent on query and return clean answer."""
    try:
        response = agent.invoke({"messages": [("user", query)]})
        for msg in reversed(response["messages"]):
            if msg.type == "ai":
                return msg.content
        return "No clear answer generated."
    except Exception as e:
        return f"Error: {str(e)}"

# if __name__ == "__main__":
#     while True:
#         user_input = input("Ask (or 'exit'): ").strip()
#         if user_input.lower() == 'exit':
#             break
#         response = get_rag_response(user_input)
#         print(f"A: {response}\n")


        
