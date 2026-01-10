import pandas as pd
import numpy as np
import math

def safe_float(value, default=None):
    """
    Converts NaN / inf to a JSON-safe value
    """
    try:
        if value is None:
            return default
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return default
        return float(value)
    except Exception:
        return default
def analyze_dataset(df: pd.DataFrame):
    analysis = {}

    # ---------------- BASIC STATS ----------------
    analysis["rows"] = df.shape[0]
    analysis["columns"] = df.shape[1]
    analysis["column_names"] = df.columns.tolist()
    analysis["data_types"] = df.dtypes.astype(str).to_dict()
    analysis["missing_values"] = df.isnull().sum().to_dict()

    # ---------------- NUMERIC DISTRIBUTIONS ----------------
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
    analysis["numeric_distributions"] = {}

    for col in numeric_cols:
         analysis["numeric_distributions"][col] = {
        "mean": safe_float(df[col].mean()),
        "median": safe_float(df[col].median()),
        "std": safe_float(df[col].std()),
        "min": safe_float(df[col].min()),
        "max": safe_float(df[col].max()),
        "skewness": safe_float(df[col].skew())
    }


    # ---------------- CATEGORICAL DISTRIBUTIONS ----------------
    categorical_cols = df.select_dtypes(include=["object", "category", "bool"]).columns
    analysis["categorical_distributions"] = {}

    for col in categorical_cols:
        top_values = df[col].value_counts().head(3).to_dict()
        analysis["categorical_distributions"][col] = top_values

    # ---------------- CORRELATIONS ----------------
    analysis["strong_correlations"] = []
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr().abs()

        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                val = corr_matrix.iloc[i, j]
                if val > 0.7:
                    analysis["strong_correlations"].append({
                        "feature_1": numeric_cols[i],
                        "feature_2": numeric_cols[j],
                        "correlation": round(val, 3)
                    })

    return analysis
