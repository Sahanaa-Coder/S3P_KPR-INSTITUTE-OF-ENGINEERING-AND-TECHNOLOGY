"""
model_trainer.py
----------------
Defines, trains, and evaluates three ML models:
  1. Logistic Regression
  2. Decision Tree Classifier
  3. Random Forest Classifier (with GridSearchCV tuning)

Also performs 5-fold cross-validation and selects the best model.
"""

import os
import time
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report,
    confusion_matrix, roc_curve
)

try:
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    TREE_MODELS_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Tree-based sklearn estimators unavailable: {e}")
    DecisionTreeClassifier = None
    RandomForestClassifier = None
    TREE_MODELS_AVAILABLE = False

if os.path.basename(os.path.dirname(__file__)) == "src":
    MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
else:
    MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


# ---------------------------------------------------------------------------
# Model definitions
# ---------------------------------------------------------------------------

def get_base_models() -> dict:
    """
    Return a dictionary of baseline sklearn estimators.

    Returns
    -------
    dict[str, estimator]
    """
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, random_state=42, solver="lbfgs"
        )
    }

    if TREE_MODELS_AVAILABLE:
        models["Decision Tree"] = DecisionTreeClassifier(
            random_state=42, max_depth=6
        )
        models["Random Forest"] = RandomForestClassifier(
            n_estimators=100, random_state=42, n_jobs=-1
        )
    else:
        models["Gaussian NB"] = GaussianNB()
        models["K-Nearest Neighbors"] = KNeighborsClassifier(n_neighbors=5)

    return models


def tune_model(X_train: np.ndarray, y_train: np.ndarray):
    """
    Tune a model using GridSearchCV (5-fold CV).

    If tree-based models are available, tune a Random Forest. Otherwise fall back
    to tuning K-Nearest Neighbors.

    Returns
    -------
    tuple[str, estimator]
        The name and the best fitted estimator.
    """
    if TREE_MODELS_AVAILABLE:
        print("\n[GridSearchCV] Tuning Random Forest ... (this may take ~30 s)")
        param_grid = {
            "n_estimators":   [50, 100, 200],
            "max_depth":      [None, 5, 10],
            "min_samples_split": [2, 5],
            "min_samples_leaf":  [1, 2],
        }
        rf = RandomForestClassifier(random_state=42, n_jobs=-1)
        grid_cv = GridSearchCV(
            rf, param_grid, cv=5, scoring="f1",
            n_jobs=-1, verbose=0, refit=True
        )
        grid_cv.fit(X_train, y_train)
        print(f"[GridSearchCV] Best params : {grid_cv.best_params_}")
        print(f"[GridSearchCV] Best CV F1  : {grid_cv.best_score_:.4f}")
        return "Random Forest (Tuned)", grid_cv.best_estimator_

    print("\n[GridSearchCV] Tree-based models unavailable. Tuning K-Nearest Neighbors instead ...")
    param_grid = {
        "n_neighbors": [3, 5, 7, 9],
        "weights": ["uniform", "distance"],
        "p": [1, 2],
    }
    knn = KNeighborsClassifier()
    grid_cv = GridSearchCV(
        knn, param_grid, cv=5, scoring="f1",
        n_jobs=-1, verbose=0, refit=True
    )
    grid_cv.fit(X_train, y_train)
    print(f"[GridSearchCV] Best params : {grid_cv.best_params_}")
    print(f"[GridSearchCV] Best CV F1  : {grid_cv.best_score_:.4f}")
    return "KNN (Tuned)", grid_cv.best_estimator_


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------

def evaluate_model(model, X_test: np.ndarray, y_test: np.ndarray,
                   model_name: str = "") -> dict:
    """
    Compute classification metrics for a fitted model.

    Parameters
    ----------
    model      : fitted sklearn estimator
    X_test     : test features
    y_test     : true labels
    model_name : display name

    Returns
    -------
    dict with accuracy, precision, recall, f1, roc_auc, confusion_matrix,
    fpr, tpr (for ROC curve), y_pred, y_prob
    """
    y_pred = model.predict(X_test)
    y_prob = (model.predict_proba(X_test)[:, 1]
              if hasattr(model, "predict_proba") else None)

    metrics = {
        "name":      model_name,
        "accuracy":  accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall":    recall_score(y_test, y_pred, zero_division=0),
        "f1":        f1_score(y_test, y_pred, zero_division=0),
        "roc_auc":   roc_auc_score(y_test, y_prob) if y_prob is not None else np.nan,
        "cm":        confusion_matrix(y_test, y_pred),
        "y_pred":    y_pred,
        "y_prob":    y_prob,
    }
    if y_prob is not None:
        metrics["fpr"], metrics["tpr"], _ = roc_curve(y_test, y_prob)

    print(f"\n--- {model_name} ---")
    print(classification_report(y_test, y_pred, target_names=["No Risk", "Risk"]))
    return metrics


def cross_validate_model(model, X_train: np.ndarray, y_train: np.ndarray,
                         model_name: str = "", cv: int = 5) -> dict:
    """
    Run k-fold cross-validation on training data.

    Parameters
    ----------
    model      : sklearn estimator (unfitted clone preferred)
    X_train    : training features
    y_train    : training labels
    model_name : display name
    cv         : number of folds

    Returns
    -------
    dict with mean and std of accuracy and f1
    """
    acc  = cross_val_score(model, X_train, y_train, cv=cv, scoring="accuracy")
    f1   = cross_val_score(model, X_train, y_train, cv=cv, scoring="f1")
    result = {
        "cv_acc_mean": acc.mean(), "cv_acc_std": acc.std(),
        "cv_f1_mean":  f1.mean(),  "cv_f1_std":  f1.std(),
    }
    print(f"[{model_name}] {cv}-Fold CV -> "
          f"Accuracy: {acc.mean():.4f} +/- {acc.std():.4f}  |  "
          f"F1: {f1.mean():.4f} +/- {f1.std():.4f}")
    return result


# ---------------------------------------------------------------------------
# Main training pipeline
# ---------------------------------------------------------------------------

def train_all_models(X_train, X_test, y_train, y_test) -> tuple:
    """
    Train, tune, and evaluate all models. Select and save the best.

    Parameters
    ----------
    X_train, X_test, y_train, y_test : preprocessed numpy arrays

    Returns
    -------
    (all_metrics, best_model, best_name, cv_results)
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    models = get_base_models()

    # --- Tune one model (Random Forest or fallback KNN) ---
    tuned_name, tuned_model = tune_model(X_train, y_train)
    models[tuned_name] = tuned_model

    print("\n========== MODEL EVALUATION ==========")
    all_metrics = {}
    cv_results  = {}

    for name, model in models.items():
        t0 = time.time()
        model.fit(X_train, y_train)
        elapsed = time.time() - t0

        metrics = evaluate_model(model, X_test, y_test, name)
        metrics["train_time"] = elapsed
        all_metrics[name] = metrics

        # Cross-validation (on training set only)
        cv_res = cross_validate_model(model, X_train, y_train, name)
        cv_results[name] = cv_res

    # --- Select best model by F1 score ---
    best_name  = max(all_metrics, key=lambda n: all_metrics[n]["f1"])
    best_model = models[best_name]
    best_f1    = all_metrics[best_name]["f1"]

    print(f"\n{'='*50}")
    print(f"  BEST MODEL : {best_name}")
    print(f"  F1 Score   : {best_f1:.4f}")
    print(f"{'='*50}")

    # --- Save best model ---
    model_path = os.path.join(MODELS_DIR, "best_model.joblib")
    joblib.dump(best_model, model_path)
    print(f"[SAVED] Best model -> {model_path}")

    return all_metrics, best_model, best_name, cv_results
