from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
import inspect


def preprocess_dataset(df, target=None):
    if target:
        X = df.drop(columns=[target])
        y = df[target]
    else:
        X = df
        y = None

    num_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    cat_cols = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    transformers = []

    if num_cols:
        transformers.append((
            "num",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ]),
            num_cols
        ))

    if cat_cols:
        # construct OneHotEncoder with the appropriate kwarg for the installed sklearn
        encoder_kwargs = {"handle_unknown": "ignore"}
        try:
            sig = inspect.signature(OneHotEncoder)
            if "sparse_output" in sig.parameters:
                encoder_kwargs["sparse_output"] = False
            elif "sparse" in sig.parameters:
                encoder_kwargs["sparse"] = False
        except Exception:
            # fallback: do not pass sparse-related kwarg
            pass

        ohe = OneHotEncoder(**encoder_kwargs)

        transformers.append((
            "cat",
            Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", ohe)
            ]),
            cat_cols
        ))

    if not transformers:
        raise ValueError("No valid columns found for preprocessing")

    preprocessor = ColumnTransformer(transformers)

    X_processed = preprocessor.fit_transform(X)

    return X_processed, y, preprocessor
