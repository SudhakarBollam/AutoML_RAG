import os
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from app.core.config import CHROMA_PATH
from app.services.target_detection import detect_target_column
from app.services.preprocessing import preprocess_dataset
from app.services.data_analysis import analyze_dataset
from app.services.recommender import recommend_models
from app.services.model_runner import train_and_evaluate_models
from app.services.rag_service import index_dataset_for_rag
from app.services.model_selection import detect_problem_type


load_dotenv()

import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def process_and_analyze_dataset(file_path: str, dataset_id: str):
    try:
        print("📊 Starting full ML pipeline for:", file_path)

        # ---------------- LOAD DATA ----------------
        df = pd.read_csv(file_path)
        if df.empty:
            raise ValueError("CSV file is empty")

        # ---------------- TARGET DETECTION ----------------
        target_info = detect_target_column(df)
        target_column = target_info[0] if isinstance(target_info, (list, tuple)) else target_info

        # ---------------- PROBLEM TYPE ----------------
        problem_type = detect_problem_type(df, target_column)

        # ---------------- PREPROCESSING ----------------
        X_processed, y, preprocessor = preprocess_dataset(
            df=df,
            target=target_column
        )

        preprocessing_steps = [
            {
                "step": "Numerical preprocessing",
                "description": "Median imputation followed by standard scaling",
                "affected_columns": df.select_dtypes(
                    include=["int64", "float64"]
                ).columns.tolist()
            },
            {
                "step": "Categorical preprocessing",
                "description": "Most-frequent imputation followed by one-hot encoding",
                "affected_columns": df.select_dtypes(
                    include=["object", "category", "bool"]
                ).columns.tolist()
            }
        ]

        # ---------------- DATA ANALYSIS ----------------
        raw_analysis = analyze_dataset(df)

        analysis = {
            "statistical_summary": {
                "total_rows": raw_analysis["rows"],
                "total_columns": raw_analysis["columns"]
            },
            "problem_type": problem_type,
            "feature_analysis": [
                {
                    "name": col,
                    "type": raw_analysis["data_types"][col],
                    "unique_values": df[col].nunique(),
                    "missing_percentage": round(
                        (raw_analysis["missing_values"][col] / raw_analysis["rows"]) * 100,
                        2
                    ),
                    "importance": "high",
                    "description": f"Feature representing {col}"
                }
                for col in df.columns
            ],
            "insights": [
                {
                    "title": "Dataset Overview",
                    "description": "Basic statistical analysis completed successfully.",
                    "importance": "high"
                }
            ]
        }

        
        # ---------------- MODEL TRAINING ----------------
        if problem_type == "unsupervised":
            model_results = {
                "all_model_metrics": []
            }
            best_model = None
        else:
            model_results = train_and_evaluate_models(
            X=X_processed,
            y=y,
            task=problem_type
        )

        if not model_results or "all_model_metrics" not in model_results:
            raise RuntimeError("Model training did not produce results")

        
        # ---------------- MODEL SELECTION ----------------
        best_model = recommend_models(
            model_results["all_model_metrics"]
        )

        # ---------------- RAG INDEXING ----------------
        os.makedirs(CHROMA_PATH, exist_ok=True)
        index_dataset_for_rag(
            file_path=file_path,
            dataset_id=dataset_id
        )

        # ---------------- FINAL RESPONSE ----------------
        response = {
            "statistical_summary": analysis["statistical_summary"],
            "problem_type": problem_type,
            "target_column": target_column,
            "best_model": best_model,
            "model_metrics": model_results["all_model_metrics"],
            "feature_analysis": analysis["feature_analysis"],
            "insights": analysis["insights"],
            "preprocessing_steps": preprocessing_steps,
            "warnings": []
        }

        print("✅ ML pipeline completed successfully")
        return response

    except Exception as e:
        print("❌ ML PIPELINE ERROR:", str(e))
        raise
