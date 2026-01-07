import os
from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.core.config import CHROMA_PATH
from langchain_ollama import OllamaEmbeddings

def index_dataset_for_rag(file_path: str, dataset_id: str):
    """Handles the embedding and persistent storage of the dataset."""
    try:
        # 1. Load and Split
        loader = CSVLoader(file_path)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=50)
        chunks = splitter.split_documents(docs)

        # 2. Initialize Embeddings
        #**************** hugging face embedding *****************************
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        

        #embeddings = OllamaEmbeddings(model="mahonzhan/all-MiniLM-L6-v2")
        # 3. Persist in ChromaDB
        vector_db = Chroma.from_documents(
            documents=chunks, 
            embedding=embeddings, 
            persist_directory=CHROMA_PATH,
            collection_name=dataset_id
        )
        return True
    except Exception as e:
        print(f"RAG Indexing Error: {e}")
        return False