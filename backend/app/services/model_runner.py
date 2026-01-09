from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import accuracy_score, f1_score, r2_score, mean_squared_error, silhouette_score
import numpy as np


def train_and_evaluate_models(X, y, task):
    results = []

    if task == "classification":
        stratify = y if y.nunique() < 0.3 * len(y) else None

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=stratify
        )

        models = {
            "LogisticRegression": LogisticRegression(max_iter=1000),
            "RandomForestClassifier": RandomForestClassifier(n_estimators=200)
        }

        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)

            results.append({
                "model": name,
                "accuracy": accuracy_score(y_test, preds),
                "f1_score": f1_score(y_test, preds, average="weighted")
            })

    elif task == "regression":
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        models = {
            "LinearRegression": LinearRegression(),
            "Ridge": Ridge(alpha=1.0),
            "RandomForestRegressor": RandomForestRegressor(n_estimators=200)
        }

        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)

            results.append({
                "model": name,
                "r2_score": r2_score(y_test, preds),
                "rmse": np.sqrt(mean_squared_error(y_test, preds))
            })

    else:
        models = {
            "KMeans": KMeans(n_clusters=3, n_init=10),
            "DBSCAN": DBSCAN(),
            "GaussianMixture": GaussianMixture(n_components=3)
        }

        for name, model in models.items():
            labels = model.fit_predict(X)

            if len(set(labels)) > 1 and -1 not in set(labels):
                score = silhouette_score(X, labels)
            else:
                score = -1

            results.append({
                "model": name,
                "silhouette_score": score
            })

    return {
    "all_model_metrics": results
}
