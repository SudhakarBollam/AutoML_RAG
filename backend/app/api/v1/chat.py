from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.core.config import CHROMA_PATH
from langchain_google_genai import ChatGoogleGenerativeAI
import requests
import json 
from dotenv import load_dotenv
import httpx
import os
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings


load_dotenv()
router = APIRouter()

class ChatRequest(BaseModel):
    dataset_id: str
    message: str

@router.post("/chat")
async def chat_with_dataset(request: ChatRequest):

    try:
        # 1. Initialize Model
     #***************** ONLY FOR OLLAMA(MISTRAL) USAGE *****************************
        model = ChatOllama(
            model="mistral:latest",
            temperature=0.7
        )
    #***************** ONLY FOR GOOGLE GENAI USAGE *****************************

        # model = ChatGoogleGenerativeAI(
        #     model="gemini-2.0-flash", 
        #     google_api_key=os.getenv("API_KEY") # Ensure this matches your .env key
        # )
    #**************** ONLY FOR OPENAI USAGE *****************************   
        # print("OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))
        # model = ChatOpenAI(
        #     model="gpt-4o-mini",
        #     temperature=0,
        #     api_key=os.getenv("OPENAI_API_KEY")
        # )
        
        # 2. Embeddings
        #**************** hugging face embedding *****************************
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        
       # embeddings = OllamaEmbeddings(model="mahonzhan/all-MiniLM-L6-v2")
        # 3. Load Vector DB
        vector_db = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings,
            collection_name=request.dataset_id,
            collection_metadata={"hnsw:space": "cosine"}
        )
        print("Collection name:", request.dataset_id)
        print("Document count:", vector_db._collection.count())
        print("CHROMA_PATH =", CHROMA_PATH)
        # 3. Simple Retrieval & Response
        docs = vector_db.similarity_search(request.message, k=3)
        
        if not docs:
            return {"answer": "I couldn't find any relevant data in this dataset to answer your question."}

        context = "\n".join([doc.page_content for doc in docs])
        
        prompt = f"""
        You are a data analysis assistant. Answer questions using less emojis . 
        Context from dataset: {context}
        
        Question: {request.message}
        
        Answer based on the provided data:"""
        
        response = model.invoke(prompt)
        return {"answer": response.content}
        
    except Exception as e:
        print(f"Error in chat: {str(e)}") # This will print to your terminal logs
        raise HTTPException(status_code=500, detail=f"VectorDB Error: {str(e)}")


#**************************ONLY FOR OPEN ROUTER USAGE **********************************

# @router.post("/chat")
# async def chat_with_dataset(request: ChatRequest):
#     try:
#         # 1. Load Vector DB
#         embeddings = HuggingFaceEmbeddings(
#             model_name="sentence-transformers/all-MiniLM-L6-v2"
#         )

#         vector_db = Chroma(
#             persist_directory=CHROMA_PATH,
#             embedding_function=embeddings,
#             collection_name=request.dataset_id
#         )

#         print("Collection:", request.dataset_id)
#         print("Docs:", vector_db._collection.count())

#         docs = vector_db.similarity_search(request.message, k=10)
#         if not docs:
#             return {"answer": "No relevant data found in this dataset."}

#         context = "\n".join(doc.page_content for doc in docs)

#         prompt = f"""
#             You are a data analysis assistant.
#                 Context from dataset:
#                 {context}

#                 Question:
#                         {request.message}
#                         Answer using ONLY the dataset context."""

        # 2. Call OpenRouter (ASYNC)
        # async with httpx.AsyncClient() as client:
        #     resp = await client.post(
        #         "https://openrouter.ai/api/v1/chat/completions",
        #         headers={
        #             "Authorization": f"Bearer {os.getenv('OPEN_ROUTER')}",
        #             "Content-Type": "application/json",
        #         },
        #         json={
        #             "model": "openai/gpt-4o-mini",
        #             "messages": [
        #                 {"role": "user", "content": prompt}
        #             ],
        #             "temperature": 0
        #         },
        #         timeout=30
        #     )

        # if resp.status_code != 200:
        #     raise Exception(resp.text)

        # answer = resp.json()["choices"][0]["message"]["content"]
        # return {"answer": answer}

    # except Exception as e:
    #     print("Chat error:", e)
    #     raise HTTPException(status_code=500, detail=str(e))