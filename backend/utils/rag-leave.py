from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
import re
import torch  # Import torch for device detection


def clean_agent_response(agent_response: str) -> str:
    import re
    cleaned = re.sub(r'<think>.*?</think>', '', agent_response, flags=re.DOTALL)
    return cleaned.strip()


# Detect device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")


# Load documents from text file
loader = TextLoader("leave-policy.txt")
docs = loader.load()


# Chunk the documents for better retrieval granularity
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)


# Create vector store with embeddings
embedding_model = OllamaEmbeddings(model="nomic-embed-text")  # Normally, device param may go here if supported
vector_store = Chroma.from_documents(splits, embedding=embedding_model)


# Initialize language model
model = ChatOllama(model="qwen3:0.6b", temperature=0.7)
# Note: If the ChatOllama or OllamaEmbeddings supports device setting, apply it here accordingly


def leave_query_rag(question: str) -> str:
    # Retrieve relevant docs
    retrieved_docs = vector_store.similarity_search(question, k=2)

    # Combine retrieved contexts
    context = "\n\n".join(doc.page_content for doc in retrieved_docs)

    prompt = (
        f"Answer the question based ONLY on the following context:\n{context}\n\n"
        f"Question: {question}\nAnswer:"
    )

    # Query language model
    response = model.invoke([{"role": "user", "content": prompt}])

    # Clean and return answer
    return clean_agent_response(response.content)


while True:
    user_question = input("Enter: ")
    if user_question.lower() == 'exit':
        break
    answer = leave_query_rag(user_question)
    print(f"Answer: {answer}\n")
