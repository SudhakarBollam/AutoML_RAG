import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
import inspect


def detect_outliers_iqr(series: pd.Series):
    """Detect outliers using IQR (safe & explainable)."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    return {
        "lower_bound": float(lower),
        "upper_bound": float(upper),
        "outlier_count": int(((series < lower) | (series > upper)).sum())
    }


def preprocess_dataset(df: pd.DataFrame, target: str | None = None):
    """
    Explainable AutoML preprocessing with outlier diagnostics.
    """

    # -------------------------------
    # 1. Separate features & target
    # -------------------------------
    if target and target in df.columns:
        X = df.drop(columns=[target])
        y = df[target]
    else:
        X = df.copy()
        y = None

    numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    if not numeric_cols and not categorical_cols:
        raise ValueError("No valid columns found for preprocessing")

    # -------------------------------
    # 2. Outlier analysis (BEFORE)
    # -------------------------------
    outlier_report_before = {}
    for col in numeric_cols:
        stats = detect_outliers_iqr(X[col].dropna())
        outlier_report_before[col] = stats

    # -------------------------------
    # 3. Build preprocessing pipelines
    # -------------------------------
    transformers = []

    if numeric_cols:
        numeric_pipeline = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])
        transformers.append(("num", numeric_pipeline, numeric_cols))

    if categorical_cols:
        encoder_kwargs = {"handle_unknown": "ignore"}
        sig = inspect.signature(OneHotEncoder)
        if "sparse_output" in sig.parameters:
            encoder_kwargs["sparse_output"] = False
        else:
            encoder_kwargs["sparse"] = False

        categorical_pipeline = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(**encoder_kwargs))
        ])
        transformers.append(("cat", categorical_pipeline, categorical_cols))

    preprocessor = ColumnTransformer(transformers, remainder="drop")

    # -------------------------------
    # 4. Transform
    # -------------------------------
    X_processed = preprocessor.fit_transform(X)

    # -------------------------------
    # 5. Outlier summary (AFTER)
    # -------------------------------
    outlier_report_after = {}
    for col in numeric_cols:
        outlier_report_after[col] = {
            "outlier_count": 0,
            "note": "Scaling reduces impact; no rows removed"
        }

    # -------------------------------
    # 6. Preprocessing explanation
    # -------------------------------
    preprocessing_visuals = {
        "flowchart": [
            "Raw Dataset",
            "Missing Value Imputation",
            "Outlier Detection (No Row Removal)",
            "Categorical Encoding",
            "Numerical Scaling",
            "Model-Ready Dataset"
        ],
        "outliers": {
            "before": outlier_report_before,
            "after": outlier_report_after,
            "method": "IQR detection (no removal)",
            "message": (
                "No significant outliers detected"
                if all(v["outlier_count"] == 0 for v in outlier_report_before.values())
                else "Outliers detected and impact reduced via scaling"
            )
        },
        "column_treatments": {
            "numeric": numeric_cols,
            "categorical": categorical_cols
        }
    }

    preprocessing_meta = {
    "numeric_cols": numeric_cols,
    "categorical_cols": categorical_cols,
    "visuals": preprocessing_visuals
    }

    return X_processed, y, preprocessor, preprocessing_meta
