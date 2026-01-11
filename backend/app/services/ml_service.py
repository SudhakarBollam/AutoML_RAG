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
from app.services.target_matching import suggest_target_columns
from app.services.target_detection import detect_target_column
from app.services.preprocessing import preprocess_dataset
from app.services.data_analysis import analyze_dataset, compute_boxplot_stats
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


def process_and_analyze_dataset(file_path: str, 
                                dataset_id: str,
                                user_target_column: str | None = None):
    try:
        print("📊 Starting full ML pipeline for:", file_path)

        # ---------------- LOAD DATA ----------------
        df = pd.read_csv(file_path)
        if df.empty:
            raise ValueError("CSV file is empty")
        
        #----------------- BOXPLOT STATS ----------------
        boxplot_stats = compute_boxplot_stats(df)

        # ---------------- TARGET DETECTION ----------------
        
        # -------------------------------
        # TARGET COLUMN RESOLUTION
        # -------------------------------
        columns = list(df.columns)

        if user_target_column:
        # Exact (case-insensitive) match
            exact_match = next(
        (c for c in columns if c.lower() == user_target_column.lower()),None)

            if exact_match:
                target_column = exact_match
                target_source = "user_exact"

            else:
                suggestions = suggest_target_columns(
                user_target_column,
                columns
        )

                # app/services/ml_service.py

                if suggestions:
                    return {
        "analysis_status": "needs_user_input", 
        "dataset_id": dataset_id,
        "message": f"Target column '{user_target_column}' not found.",
        "user_input": user_target_column,
        "suggested_targets": suggestions,
        "columns": columns,
        # Add these to prevent frontend "undefined" errors
        "analysis_result": {
            "preprocessing_report": {"flow": []}, # Prevents .join() errors on flow
            "insights": [],
            "feature_analysis": []
        }
    }

        # No suggestions → fallback
                target_column = detect_target_column(df)
                target_source = "auto_fallback"

        else:
            target_column = detect_target_column(df)
            target_source = "auto"

        analysis_result = {
            "dataset_id": dataset_id,
            "analysis_status": "completed",
            "target_column": target_column,
            "target_source": target_source,
            "columns": columns,
        }
        analysis_result["columns"] = list(df.columns)
        # ---------------- PROBLEM TYPE ----------------
        problem_type = detect_problem_type(df, target_column)

        # ---------------- PREPROCESSING ----------------
        X_processed, y, preprocessor, preprocessing_meta = preprocess_dataset(df, target_column)

        numeric_cols = preprocessing_meta["numeric_cols"]
        categorical_cols = preprocessing_meta["categorical_cols"]
        preprocessing_visuals = preprocessing_meta["visuals"]

        # ---------------- PREPROCESSING REPORT ----------------
        numeric_cols = preprocessing_meta["numeric_cols"]
        categorical_cols = preprocessing_meta["categorical_cols"]

        preprocessing_flow = [
        {"step": 1, "label": "Raw Dataset"},
        {"step": 2, "label": "Missing Value Imputation"},
        {"step": 3, "label": "Outlier Detection (No Row Removal)"},
        {"step": 4, "label": "Categorical Encoding"},
        {"step": 5, "label": "Numerical Scaling"},
        {"step": 6, "label": "Model-Ready Dataset"}
        ]

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
        #-----------------COLUMN TRASNSFORMATION DETAILS ----------------

        column_transformations = []

        for col in df.columns:
            if col == target_column:
                continue

            col_info = {
                "column": col,
                "missing_handling": "None",
                "scaling": "None",
                "encoding": "None",
                "outlier_handling": "Detected only (no removal)"
            }

            if df[col].isna().any():
                col_info["missing_handling"] = (
                    "Median Imputation" if col in numeric_cols
                    else "Most Frequent Imputation"
                )

            if col in numeric_cols:
                if df[col].nunique() > 2:
                    col_info["scaling"] = "StandardScaler"
                else:
                    col_info["scaling"] = "Skipped (binary feature)"

            if col in categorical_cols:
                col_info["encoding"] = "One-Hot Encoding"

            column_transformations.append(col_info)



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
            "boxplot_stats": boxplot_stats,
            "column_transformations": column_transformations,
            "preprocessing_flow": preprocessing_flow,
            "missing_summary": missing_summary,
            "preprocessing_visuals": preprocessing_visuals,
            "numeric_distributions": raw_analysis["numeric_distributions"],
            "insights": analysis["insights"],
            "preprocessing_steps": preprocessing_steps,
            "warnings": []
        }

        print("✅ ML pipeline completed successfully")
        return {
    "analysis_status": "completed",
    "dataset_id": dataset_id,
    "analysis_result": response
}

    except Exception as e:
        print("❌ ML PIPELINE ERROR:", str(e))
        raise

