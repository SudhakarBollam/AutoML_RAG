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


def _name_score(col_name: str) -> int:
    name = col_name.lower()
    if name in ("target", "label", "y", "outcome"):
        return 6
    if re.search(r"death|deceased|mortality|mortality_rate|died|death_event|outcome", name):
        return 5
    if re.search(r"surviv|passed|event", name):
        return 3
    return 0


def detect_target_column(df: pd.DataFrame):
    """Heuristic target detection.

    Strategy:
    - Exclude constant, identifier (unique per row), and datetime columns.
    - Score columns by name hints, data type, unique-count ratios.
    - If sklearn is available, add a mutual-information signal between candidate and other columns.
    - Pick highest-scoring candidate above a threshold, and classify as 'classification' or 'regression'.
    """
    if not isinstance(df, pd.DataFrame) or df.shape[1] == 0:
        return None, "unsupervised"

    n_rows = df.shape[0]
    candidates = []

    for col in df.columns:
        series = df[col]

        # Skip unusable columns
        if series.nunique(dropna=False) <= 1:
            continue
        if series.nunique(dropna=False) == n_rows:
            continue
        if pd.api.types.is_datetime64_any_dtype(series):
            continue

        candidates.append(col)

    if not candidates:
        return None, "unsupervised"

    scores = {}

    # Prepare data for mutual information if available
    mi_cache = {}
    if _SKLEARN_AVAILABLE and len(candidates) >= 1 and df.shape[1] > 1:
        # Build a feature matrix of other columns encoded to numeric
        feature_cols = [c for c in df.columns if c in df.columns]
        X_enc = pd.DataFrame()
        for c in feature_cols:
            s = df[c]
            if pd.api.types.is_numeric_dtype(s):
                X_enc[c] = s.fillna(s.median() if s.dropna().size else 0)
            else:
                le = LabelEncoder()
                try:
                    X_enc[c] = le.fit_transform(s.fillna("<NA>").astype(str))
                except Exception:
                    X_enc[c] = pd.factorize(s.fillna("<NA>").astype(str))[0]

        imputer = SimpleImputer(strategy="median")
        try:
            X_num = imputer.fit_transform(X_enc)
        except Exception:
            X_num = X_enc.fillna(-999).values

    for col in candidates:
        series = df[col]
        col_score = 0

        # Name hint
        col_score += _name_score(col)

        nunique = series.nunique(dropna=False)
        unique_ratio = nunique / max(1, n_rows)

        # Type-based scoring
        if pd.api.types.is_bool_dtype(series) or nunique == 2:
            col_score += 5
        elif not pd.api.types.is_numeric_dtype(series):
            # categorical/text-like
            if nunique <= 20:
                col_score += 4
            else:
                col_score += 1
        else:
            # numeric
            if nunique <= 5:
                col_score += 4
            elif nunique <= 30:
                col_score += 3
            else:
                col_score += 2

        # Unique-ratio penalties/bonuses (prefer not-all-unique and not too-sparse)
        if unique_ratio < 0.01:
            col_score += 1
        if unique_ratio > 0.95:
            col_score -= 3

        # Mutual information signal (how informative this column is relative to others)
        if _SKLEARN_AVAILABLE and df.shape[1] > 1:
            try:
                other_idx = [i for i, c in enumerate(feature_cols) if c != col]
                if other_idx:
                    X_for_mi = X_num[:, other_idx]
                    y_col = df[col]

                    # Coerce to numeric when possible and decide whether to use
                    # regression or classification MI based on dtype and uniqueness.
                    y_num = pd.to_numeric(y_col, errors="coerce")
                    n_unique = y_col.nunique(dropna=True)

                    try:
                        if pd.api.types.is_numeric_dtype(y_num) and y_num.dropna().nunique() > 10:
                            mi = mutual_info_regression(X_for_mi, y_num.fillna(y_num.median()).values)
                            mi_score = float(np.mean(mi))
                        elif n_unique > 0.5 * n_rows:
                            # many unique values -> likely regression-like
                            if y_num.dropna().size:
                                mi = mutual_info_regression(X_for_mi, y_num.fillna(y_num.median()).values)
                                mi_score = float(np.mean(mi))
                            else:
                                y_enc = LabelEncoder().fit_transform(y_col.fillna("<NA>").astype(str))
                                mi = mutual_info_classif(X_for_mi, y_enc)
                                mi_score = float(np.mean(mi))
                        else:
                            # treat as categorical
                            y_enc = LabelEncoder().fit_transform(y_col.fillna("<NA>").astype(str))
                            mi = mutual_info_classif(X_for_mi, y_enc)
                            mi_score = float(np.mean(mi))

                        # scale and add
                        col_score += min(5, mi_score * 5)
                    except Exception:
                        # ignore MI failures, keep heuristic scores
                        pass
            except Exception:
                # ignore MI failures, keep heuristic scores
                pass

        scores[col] = col_score

    # Choose best candidate
    best_col = max(scores, key=scores.get)
    best_score = scores[best_col]

    # Threshold: require a reasonable score to accept a supervised target
    if best_score < 4:
        return None, "unsupervised"

    # Determine problem type
    y = df[best_col]
    nunique = y.nunique(dropna=False)

    if pd.api.types.is_numeric_dtype(y):
        if nunique <= 10:
            problem = "classification"
        else:
            problem = "regression"
    else:
        problem = "classification"

    return best_col, problem
