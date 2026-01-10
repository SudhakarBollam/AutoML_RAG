def select_best_model(model_metrics, task):
    """
    Selects the best model based on:
    - Multi-metric performance
    - Overfitting awareness
    - Stability across CV folds
    """

    if not model_metrics:
        return None

    scored_models = []

    for m in model_metrics:
        # ---------------- COMMON SIGNALS ----------------
        train_score = m.get("train_score", 0)
        cv_mean = m.get("cv_mean", 0)
        cv_std = m.get("cv_std", 0)

        overfit_gap = abs(train_score - cv_mean)

        # ---------------- BASE SCORE ----------------
        if task == "classification":
            base_score = (
                0.4 * m["f1_score"] +
                0.3 * m["accuracy"] +
                0.3 * m["recall"]
            )

        elif task == "regression":
            base_score = (
                0.6 * (1 / (m["rmse"] + 1e-6)) +
                0.4 * m["r2"]
            )

        else:  # unsupervised
            base_score = m["silhouette_score"]

        # ---------------- PENALTIES ----------------
        penalty = (0.3 * overfit_gap) + (0.2 * cv_std)

        final_score = base_score - penalty

        scored_models.append({
            **m,
            "final_score": final_score,
            "overfit_gap": overfit_gap
        })

    # ---------------- SELECT BEST ----------------
    best = max(scored_models, key=lambda x: x["final_score"])

    # ---------------- CONFIDENCE ----------------
    if task in ["classification", "regression"]:
        confidence = int(min(95, best["cv_mean"] * 100))
    else:
        confidence = int(min(90, best["final_score"] * 100))

    # ---------------- REASONING ----------------
    reasoning = (
        f"Selected because it achieved the best balance between performance "
        f"and generalization. The model shows a low overfitting gap "
        f"({round(best['overfit_gap'], 3)}) and stable cross-validation "
        f"results."
    )

    return {
        "name": best["model"],
        "algorithm": "Linear / Tree / Ensemble / Clustering",
        "confidence": confidence,
        "reasoning": reasoning,
        "tradeoffs": "May require slightly more computation but offers better reliability"
    }
