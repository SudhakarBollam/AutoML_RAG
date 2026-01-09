def recommend_models(results):
    if not results:
        return None

    if "accuracy" in results[0]:
        return max(results, key=lambda x: x["accuracy"])

    if "r2_score" in results[0]:
        return max(results, key=lambda x: x["r2_score"])

    if "silhouette_score" in results[0]:
        return max(results, key=lambda x: x["silhouette_score"])

    return None
