import os
from datetime import datetime
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

from langchain_core.documents import Document
import faiss

# Initialize FastEmbed embeddings (lightweight, CPU-based, no PyTorch)
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


# Create a data directory in the current workspace
data_dir = os.path.join(os.path.dirname(__file__), "..", "datastore")
os.makedirs(data_dir, exist_ok=True)

# Initialize FAISS index with the correct dimension from embedding size
embedding_dim = len(embedding_function.embed_query("test"))
index = faiss.IndexFlatL2(embedding_dim)

# Initialize FAISS vector store with a proper in-memory docstore
vector_store = FAISS(
    embedding_function=embedding_function,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)


# 1. Add to long-term with metadata
def add_to_long_term(text, metadata=None):
    metadata = metadata or {}
    metadata.setdefault("date", datetime.now().strftime("%Y-%m-%d"))
    metadata.setdefault("type", "chat")
    doc = Document(page_content=text, metadata=metadata)
    vector_store.add_documents([doc])
    # Note: FAISS does not have a built-in persist method; you can save manually if needed

# 2. Search long-term memory
def search_long_term(query, k=4):
    results = vector_store.similarity_search(query, k=k)
    return [(doc.page_content, doc.metadata) for doc in results]

# Optional: Save and load FAISS index manually if persistence is needed
def save_faiss_index(path):
    vector_store.index.save_local(path)

def load_faiss_index(path):
    vector_store.index = faiss.read_index(path)

