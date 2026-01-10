import re
import pandas as pd
import numpy as np

try:
    from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
    from sklearn.preprocessing import LabelEncoder
    from sklearn.impute import SimpleImputer
    _SKLEARN_AVAILABLE = True
except Exception:
    _SKLEARN_AVAILABLE = False


# =====================================================
# SEMANTIC KNOWLEDGE BASE
# =====================================================
TARGET_KEYWORDS = {
    "generic": [
        "target", "label", "class", "output", "result", "y", "response",
        "prediction", "predicted", "outcome", "status", "flag", "decision",
        "category", "type"
    ],
    "events": [
        "event", "death", "deceased", "default", "churn", "fraud", "failure",
        "survived", "passed", "dropout", "termination", "incident",
        "occurrence", "accident", "collapse"
    ],
    "business": [
        "price", "sales", "revenue", "profit", "loss", "cost", "income",
        "margin", "turnover", "demand", "supply", "growth", "roi",
        "valuation", "expense"
    ],
    "medical": [
        "mortality", "diagnosis", "diabetes", "death", "survival",
        "disease", "outcome", "prognosis", "recovery", "severity",
        "risk", "condition", "treatment", "complication", "relapse"
    ],
    "finance": [
        "credit", "loan", "risk", "score", "default", "balance", "debt",
        "liability", "asset", "equity", "interest", "payment", "installment",
        "limit", "exposure"
    ],
    "education": [
        "grade", "score", "marks", "result", "pass", "fail", "rank",
        "performance", "gpa", "cgpa", "outcome", "completion",
        "dropout", "evaluation", "assessment"
    ]
}


# =====================================================
# DOMAIN INFERENCE
# =====================================================
def infer_domain(columns):
    text = " ".join(columns).lower()

    if any(k in text for k in ["creatinine", "platelets", "serum", "blood"]):
        return "medical"
    if any(k in text for k in ["price", "revenue", "sales", "profit"]):
        return "business"
    if any(k in text for k in ["loan", "credit", "default", "balance"]):
        return "finance"
    if any(k in text for k in ["grade", "marks", "gpa"]):
        return "education"

    return "generic"


# =====================================================
# SEMANTIC NAME SCORE
# =====================================================
def semantic_score(col_name: str) -> int:
    name = col_name.lower()
    score = 0
    for group in TARGET_KEYWORDS.values():
        for word in group:
            if word in name:
                score += 6
    return score


# =====================================================
# STATISTICAL SCORE
# =====================================================
def statistical_score(df: pd.DataFrame, col: str) -> float:
    s = df[col]
    n = len(s)
    score = 0

    # Eliminate ID-like columns
    if s.nunique(dropna=False) == n:
        return -1000

    # Missing values (targets usually dense)
    if s.isnull().mean() < 0.1:
        score += 2

    # Cardinality heuristics
    unique_ratio = s.nunique(dropna=True) / max(1, n)
    if unique_ratio < 0.05:
        score += 3
    elif unique_ratio > 0.9:
        score -= 4

    # Type preference
    if pd.api.types.is_bool_dtype(s) or s.nunique() == 2:
        score += 5
    elif not pd.api.types.is_numeric_dtype(s):
        score += 3
    else:
        if s.nunique() <= 10:
            score += 4
        elif s.nunique() <= 30:
            score += 3
        else:
            score += 2

    return score


# =====================================================
# FINAL TARGET DETECTION (MERGED LOGIC)
# =====================================================
def detect_target_column(df: pd.DataFrame):
    """
    Detects the most likely target column using:
    - Semantic knowledge base
    - Domain priors
    - Statistical heuristics
    - Mutual Information (if sklearn available)

    Returns:
        best_target_column (str) or None
    """

    if not isinstance(df, pd.DataFrame) or df.shape[1] == 0:
        return None

    n_rows = df.shape[0]
    domain = infer_domain(df.columns)
    scores = {}

    # ---------------- Prepare MI feature matrix ----------------
    if _SKLEARN_AVAILABLE and df.shape[1] > 1:
        X_enc = pd.DataFrame()
        for c in df.columns:
            s = df[c]
            if pd.api.types.is_numeric_dtype(s):
                X_enc[c] = s.fillna(s.median() if s.dropna().size else 0)
            else:
                try:
                    X_enc[c] = LabelEncoder().fit_transform(
                        s.fillna("<NA>").astype(str)
                    )
                except Exception:
                    X_enc[c] = pd.factorize(s.fillna("<NA>").astype(str))[0]

        try:
            X_num = SimpleImputer(strategy="median").fit_transform(X_enc)
        except Exception:
            X_num = X_enc.fillna(-999).values
    else:
        X_num = None

    # ---------------- Score each column ----------------
    for idx, col in enumerate(df.columns):
        s = df[col]

        # Exclusions
        if s.nunique(dropna=False) <= 1:
            continue
        if s.nunique(dropna=False) == n_rows:
            continue
        if pd.api.types.is_datetime64_any_dtype(s):
            continue

        score = 0

        # 1️⃣ Semantic knowledge base
        score += semantic_score(col)

        # 2️⃣ Statistical heuristics
        score += statistical_score(df, col)

        # 3️⃣ Domain prior boost
        if domain in TARGET_KEYWORDS:
            if any(k in col.lower() for k in TARGET_KEYWORDS[domain]):
                score += 5

        # 4️⃣ Mutual Information signal (optional, strong)
        if _SKLEARN_AVAILABLE and X_num is not None:
            try:
                other_idx = [i for i in range(X_num.shape[1]) if i != idx]
                if other_idx:
                    X_other = X_num[:, other_idx]
                    y_col = df[col]

                    y_num = pd.to_numeric(y_col, errors="coerce")
                    n_unique = y_col.nunique(dropna=True)

                    if pd.api.types.is_numeric_dtype(y_num) and n_unique > 10:
                        mi = mutual_info_regression(
                            X_other,
                            y_num.fillna(y_num.median()).values
                        )
                    else:
                        y_enc = LabelEncoder().fit_transform(
                            y_col.fillna("<NA>").astype(str)
                        )
                        mi = mutual_info_classif(X_other, y_enc)

                    score += min(5, float(np.mean(mi)) * 5)
            except Exception:
                pass  # MI is optional, never fatal

        scores[col] = score

    if not scores:
        return None

    # ---------------- Select best ----------------
    best_col = max(scores, key=scores.get)

    # Safety threshold
    if scores[best_col] < 6:
        return None

    return best_col