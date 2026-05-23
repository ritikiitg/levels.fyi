"""Train Isolation Forest + Random Forest on the synthetic dataset.

Saves a bundle {iforest, rf, confusion, classification_report} to
app/detection/model.pkl so the scorer can load it.
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from .generate_dataset import OUT as DATASET_PATH, generate

MODEL_OUT = Path(__file__).resolve().parent.parent / "app" / "detection" / "model.pkl"


def main(n: int = 50_000) -> None:
    if not DATASET_PATH.exists():
        generate(n)
    df = pd.read_csv(DATASET_PATH)
    y = df["label"].values
    X = df.drop(columns=["label"]).values
    feature_names = list(df.drop(columns=["label"]).columns)

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    rf = RandomForestClassifier(
        n_estimators=200, max_depth=12, n_jobs=-1, random_state=42,
        class_weight="balanced",
    )
    rf.fit(X_tr, y_tr)

    # Unsupervised anomaly detector — useful when we have no label.
    iforest = IsolationForest(
        n_estimators=200, contamination=0.45, random_state=42, n_jobs=-1,
    )
    iforest.fit(X_tr)

    y_pred = rf.predict(X_te)
    cm = confusion_matrix(y_te, y_pred).tolist()
    report = classification_report(y_te, y_pred, output_dict=True, zero_division=0)

    print("Confusion matrix [[TN, FP], [FN, TP]]:", cm)
    print("Classification report:")
    print(classification_report(y_te, y_pred, zero_division=0))
    print("\nTop feature importances:")
    for name, imp in sorted(zip(feature_names, rf.feature_importances_),
                            key=lambda x: -x[1])[:10]:
        print(f"  {name:25s} {imp:.4f}")

    bundle = {
        "rf": rf,
        "iforest": iforest,
        "feature_names": feature_names,
        "confusion": cm,
        "report": report,
        "feature_importances": dict(zip(feature_names, rf.feature_importances_.tolist())),
    }
    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, MODEL_OUT)
    print(f"\nSaved model bundle to {MODEL_OUT}")


if __name__ == "__main__":
    main()
