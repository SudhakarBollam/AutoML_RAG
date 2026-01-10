from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
#sudhakar
from app.api.v1 import chat
from app.services.ml_service import process_and_analyze_dataset
from app.services.rag_service import index_dataset_for_rag

app = FastAPI()

# -----------------------------
# In-memory dataset store
# -----------------------------
# (OK for now, you already confirmed this is fine)
dataset_db = {}

# -----------------------------
# Routers
# -----------------------------
app.include_router(chat.router, prefix="/api/v1")

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Background RAG task
# -----------------------------
def run_rag_background(file_path: str, dataset_id: str):
    try:
        dataset_db[dataset_id]["rag_status"] = "indexing"

        success = index_dataset_for_rag(file_path, dataset_id)

        dataset_db[dataset_id]["rag_status"] = (
            "ready" if success else "failed"
        )

    except Exception as e:
        print(f"RAG error for {dataset_id}: {e}")
        dataset_db[dataset_id]["rag_status"] = "failed"


# -----------------------------
# Upload + Analysis endpoint
# -----------------------------
@app.post("/api/v1/upload")
async def upload_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    dataset_id = str(uuid.uuid4())
    temp_path = f"app/data/raw/{dataset_id}_{file.filename}"

    os.makedirs("app/data/raw", exist_ok=True)

    content = await file.read()
    file_size = len(content)

    if not content:
        raise ValueError("Uploaded file is empty")

    with open(temp_path, "wb") as buffer:
        buffer.write(content)

    print("📁 Saved file size:", os.path.getsize(temp_path), "bytes")
    # Initialize dataset state
    dataset_db[dataset_id] = {
        "id": dataset_id,
        "name": file.filename,
        "file_size": file_size,
        # analysis
        "analysis_status": "analyzing",
        "analysis_result": None,

        # rag
        "rag_status": "pending",
    }

    try:
        # -----------------------------
        # FAST analysis (blocking but quick)
        # -----------------------------
        analysis_result = process_and_analyze_dataset(
                file_path=temp_path,
                dataset_id=dataset_id
            )

        dataset_db[dataset_id]["analysis_status"] = "completed"
        dataset_db[dataset_id]["analysis_result"] = analysis_result

        # -----------------------------
        # SLOW RAG (background)
        # -----------------------------
        background_tasks.add_task(
            run_rag_background,
            temp_path,
            dataset_id
        )

    except Exception as e:
        print(f"Analysis error for {dataset_id}: {e}")
        dataset_db[dataset_id]["analysis_status"] = "failed"
        dataset_db[dataset_id]["error_message"] = str(e)

    return dataset_db[dataset_id]


# -----------------------------
# Dataset status endpoint
# -----------------------------
@app.get("/api/v1/dataset/{dataset_id}")
async def get_status(dataset_id: str):
    return dataset_db.get(dataset_id)