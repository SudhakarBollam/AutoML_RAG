from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    r2_score,
    mean_squared_error,
    confusion_matrix,
    silhouette_score
)
import numpy as np


def train_and_evaluate_models(X, y=None, task="classification"):
    results = []

    # ---------------- SUPERVISED ----------------
    if task in ["classification", "regression"]:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    # ---------------- CLASSIFICATION ----------------
    if task == "classification":
        models = {
            "Logistic Regression": LogisticRegression(max_iter=1000),
            "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        }

        for name, model in models.items():
            model.fit(X_train, y_train)

            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            train_acc = accuracy_score(y_train, y_train_pred)
            test_acc = accuracy_score(y_test, y_test_pred)
            precision = precision_score(y_test, y_test_pred, average="weighted")
            f1 = f1_score(y_test, y_test_pred, average="weighted")
            recall = recall_score(y_test, y_test_pred, average="weighted")
            cm = confusion_matrix(y_test, y_test_pred)

            cv_scores = cross_val_score(
                model, X, y, cv=5, scoring="f1_weighted"
            )

            results.append({
                "model": name,
                "accuracy": float(test_acc),
                "f1_score": float(f1),
                "precision": float(precision),
                "recall": float(recall),
                "train_score": float(train_acc),
                "cv_mean": float(np.mean(cv_scores)),
                "cv_std": float(np.std(cv_scores)),
                "confusion_matrix": cm.tolist()
            })

    # ---------------- REGRESSION ----------------
    elif task == "regression":
        models = {
            "Linear Regression": LinearRegression(),
            "Ridge Regression": Ridge(),
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        }

        for name, model in models.items():
            model.fit(X_train, y_train)

            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            rmse = rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
            r2 = r2_score(y_test, y_test_pred)

            cv_scores = cross_val_score(
                model, X, y, cv=5, scoring="r2"
            )

            results.append({
                "model": name,
                "rmse": float(rmse),
                "r2": float(r2),
                "train_score": float(model.score(X_train, y_train)),
                "cv_mean": float(np.mean(cv_scores)),
                "cv_std": float(np.std(cv_scores))
            })

    # ---------------- UNSUPERVISED ----------------
    else:
        models = {
            "KMeans": KMeans(n_clusters=3, random_state=42),
            "Gaussian Mixture": GaussianMixture(n_components=3),
        }

        for name, model in models.items():
            labels = model.fit_predict(X)
            score = silhouette_score(X, labels)

            results.append({
                "model": name,
                "silhouette_score": float(score)
            })

    return {"all_model_metrics": results}

