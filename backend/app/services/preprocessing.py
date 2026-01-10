from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
import pandas as pd
import inspect


def preprocess_dataset(df: pd.DataFrame, target: str | None = None):
    """
    Conservative, reliable preprocessing for AutoML.

    - Handles missing values safely
    - Encodes categorical variables
    - Scales numeric features
    - Keeps feature meaning intact
    - Returns reusable preprocessor
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

    # -------------------------------
    # 2. Identify column types
    # -------------------------------
    numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = X.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    if not numeric_cols and not categorical_cols:
        raise ValueError("No valid columns found for preprocessing")

    transformers = []

    # -------------------------------
    # 3. Numeric preprocessing
    # -------------------------------
    # WHY:
    # - Median handles outliers better than mean
    # - Scaling helps distance-based & linear models
    if numeric_cols:
        numeric_pipeline = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])

        transformers.append((
            "num",
            numeric_pipeline,
            numeric_cols
        ))

    # -------------------------------
    # 4. Categorical preprocessing
    # -------------------------------
    # WHY:
    # - Most frequent keeps domain meaning
    # - OneHotEncoder is safe and interpretable
    # - handle_unknown prevents runtime crashes
    if categorical_cols:
        encoder_kwargs = {"handle_unknown": "ignore"}

        # sklearn compatibility handling
        try:
            sig = inspect.signature(OneHotEncoder)
            if "sparse_output" in sig.parameters:
                encoder_kwargs["sparse_output"] = False
            elif "sparse" in sig.parameters:
                encoder_kwargs["sparse"] = False
        except Exception:
            pass

        categorical_pipeline = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(**encoder_kwargs))
        ])

        transformers.append((
            "cat",
            categorical_pipeline,
            categorical_cols
        ))

    # -------------------------------
    # 5. ColumnTransformer
    # -------------------------------
    # remainder='drop' is SAFE here because:
    # - we explicitly included all detected columns
    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop"
    )

    # -------------------------------
    # 6. Fit & transform
    # -------------------------------
    X_processed = preprocessor.fit_transform(X)

    return X_processed, y, preprocessor
