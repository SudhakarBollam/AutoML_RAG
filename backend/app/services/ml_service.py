import os
import math
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
from app.services.model_selection import select_best_model
from app.services.model_runner import train_and_evaluate_models
from app.services.rag_service import index_dataset_for_rag
from app.services.problem_detection import detect_problem_type


load_dotenv()

import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
def safe_float(v):
    if v is None:
        return None
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return float(v)


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
        # ---------------- PREPROCESSING REPORT ----------------
        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
        categorical_cols = df.select_dtypes(
            include=["object", "category", "bool"]
        ).columns.tolist()

        preprocessing_report = {
            "flow": [
                "Raw Dataset",
                "Missing Value Handling",
                "Categorical Encoding",
                "Numerical Scaling",
                "Model Ready Dataset"
            ],
            "numeric_strategy": "Median Imputation + Standard Scaling",
            "categorical_strategy": "Most Frequent Imputation + One-Hot Encoding",
            "numeric_features": numeric_cols,
            "categorical_features": categorical_cols,
            "total_features_before": int(df.shape[1] - 1),
            "total_features_after": int(X_processed.shape[1])
        }
        missing_summary = {
            col: int(df[col].isna().sum())
            for col in df.columns
            if df[col].isna().sum() > 0
        }

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
        insights = []

        #Missing data insight
        for col, missing in raw_analysis["missing_values"].items():
            pct = round((missing / raw_analysis["rows"]) * 100, 2)
            if pct > 30:
                insights.append({
                    "title": "High Missing Values",
                    "description": f"Column '{col}' has {pct}% missing values.",
                    "importance": "high"
                })

        #Skewness insight
        for col, stats in raw_analysis.get("numeric_distributions", {}).items():
            if abs(stats["skewness"]) > 1:
                insights.append({
                    "title": "Skewed Distribution",
                    "description": f"Feature '{col}' is highly skewed (skewness={stats['skewness']}).",
                    "importance": "medium"
                })

        #Correlation insights
        for corr in raw_analysis.get("strong_correlations", []):
            insights.append({
                "title": "Strong Feature Relationship",
                "description": f"{corr['feature_1']} is strongly correlated with {corr['feature_2']} (corr={corr['correlation']}).",
                "importance": "high"
            })

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
            "insights": insights
        }

        

        # ---------------- MODEL TRAINING ----------------
        if problem_type == "unsupervised":
            model_results = train_and_evaluate_models(
                X=X_processed,
                task="unsupervised"
            )

            best_model = select_best_model(
                model_results["all_model_metrics"],
                problem_type
            )

        else:
            model_results = train_and_evaluate_models(
                X=X_processed,
                y=y,
                task=problem_type
            )

            best_model = select_best_model(
                model_results["all_model_metrics"],
                problem_type
            )

        if not model_results or "all_model_metrics" not in model_results:
            raise RuntimeError("Model training did not produce results")

        
        # ---------------- MODEL SELECTION ----------------
        best_model = select_best_model(
            model_results["all_model_metrics"],
            problem_type
        )
        if best_model is None:
            best_model = {
                "name": "N/A",
                "algorithm": "Unsupervised",
                "confidence": 0,
                "reasoning": "No supervised target detected. Clustering models were applied.",
                "tradeoffs": "No ground truth available for supervised evaluation."
            }
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
            "preprocessing_report": preprocessing_report,
            "missing_summary": missing_summary,
            "numeric_distributions": raw_analysis["numeric_distributions"],
            "insights": analysis["insights"],
            "preprocessing_steps": preprocessing_steps,
            "warnings": []
        }

        print("✅ ML pipeline completed successfully")
        return response

    except Exception as e:
        print("❌ ML PIPELINE ERROR:", str(e))
        raise

