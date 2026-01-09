def detect_problem_type(df, target_column):
    """
    Determines whether the ML task is:
    - classification
    - regression
    - unsupervised

    Uses robust heuristics suitable for AutoML systems.
    """

    # --------------------------------------------------
    # 1. No valid target → UNSUPERVISED
    # --------------------------------------------------
    if (
        target_column is None
        or target_column not in df.columns
        or df[target_column].dropna().empty
    ):
        return "unsupervised"

    target = df[target_column].dropna()
    total_rows = len(target)

    # Safety
    if total_rows == 0:
        return "unsupervised"

    # --------------------------------------------------
    # 2. Cardinality ratio (MOST IMPORTANT SIGNAL)
    # --------------------------------------------------
    unique_count = target.nunique()
    unique_ratio = unique_count / total_rows

    # If almost every value is unique → ID-like → unsupervised
    if unique_ratio > 0.90:
        return "unsupervised"

    # --------------------------------------------------
    # 3. Non-numeric targets → CLASSIFICATION
    # --------------------------------------------------
    if target.dtype in ["object", "bool", "category"]:
        return "classification"

    # --------------------------------------------------
    # 4. Numeric targets
    # --------------------------------------------------

    # Binary classification
    if unique_count == 2:
        return "classification"

    # Low-cardinality numeric labels (ordinal / multiclass)
    if unique_count <= 20:
        return "classification"

    # --------------------------------------------------
    # 5. Continuous numeric target → REGRESSION
    # --------------------------------------------------
    return "regression"