"""
main.py
-------
Orchestrates the full Heart Disease Predictive Modeling pipeline:
  1. Load & preprocess data
  2. Exploratory Data Analysis
  3. Train & evaluate models (LR, DT, RF + tuned RF)
  4. Generate all visualizations
  5. Save best model + scaler
  6. Demo prediction

Run:
    python main.py             # full pipeline + demo prediction
    python main.py --predict   # interactive prediction prompt
"""

import os
import sys
import argparse
import warnings
import joblib
warnings.filterwarnings("ignore")

# Make sure the project root is importable regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_heart_disease_data, preprocess_data
from eda import run_eda
from model_trainer import get_base_models, tune_model, train_all_models
from visualizer import generate_all_visualizations
from predictor import demo_predict, interactive_predict


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
MODELS_DIR = os.path.dirname(os.path.abspath(__file__))


def print_banner():
    print("""
+--------------------------------------------------------------+
|       Predictive Modeling Using Machine Learning             |
|       Heart Disease Risk Classification                      |
|       CodeAlpha Internship Project  |  Sahanaa               |
+--------------------------------------------------------------+
    """)


def print_summary(all_metrics: dict, best_name: str, cv_results: dict):
    """Print a clean summary table of all model results."""
    print("\n" + "=" * 72)
    print(f"{'MODEL':<30} {'ACC':>6} {'PREC':>6} {'REC':>6} {'F1':>6} {'AUC':>7}")
    print("-" * 72)
    for name, m in all_metrics.items():
        marker = "  <- BEST" if name == best_name else ""
        auc = f"{m['roc_auc']:.4f}" if m['roc_auc'] == m['roc_auc'] else "  N/A"
        print(f"{name:<30} {m['accuracy']:.4f} {m['precision']:.4f} "
              f"{m['recall']:.4f} {m['f1']:.4f} {auc}{marker}")
    print("=" * 72)

    print("\n5-Fold Cross-Validation Summary:")
    print(f"{'MODEL':<30} {'CV-ACC (mean±std)':>22} {'CV-F1 (mean±std)':>22}")
    print("-" * 72)
    for name, cv in cv_results.items():
        print(f"{name:<30} "
              f"{cv['cv_acc_mean']:.4f} +- {cv['cv_acc_std']:.4f}          "
              f"{cv['cv_f1_mean']:.4f} +- {cv['cv_f1_std']:.4f}")
    print("=" * 72)


def run_pipeline(interactive: bool = False):
    print_banner()

    # -- 1. Data ----------------------------------------------------------
    print("\n[STEP 1/5] Loading and preprocessing data ...")
    df = load_heart_disease_data()
    print(f"  Dataset shape : {df.shape}")
    print(f"  Columns       : {list(df.columns)}")

    X_train, X_test, y_train, y_test, scaler, feature_names = preprocess_data(df)

    # Save scaler for later inference
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.joblib"))
    joblib.dump(feature_names, os.path.join(MODELS_DIR, "feature_names.joblib"))

    # -- 2. EDA -----------------------------------------------------------
    print("\n[STEP 2/5] Running Exploratory Data Analysis ...")
    eda_paths = run_eda(df)

    # -- 3. Train models --------------------------------------------------
    print("\n[STEP 3/5] Training and evaluating models ...")
    all_metrics, best_model, best_name, cv_results = train_all_models(
        X_train, X_test, y_train, y_test
    )

    # -- 4. Visualizations ------------------------------------------------
    print("\n[STEP 4/5] Generating model evaluation visualizations ...")

    # Reconstruct named model dict (needed for feature-importance plot)
    base_models = get_base_models()
    tuned_name, tuned_model = tune_model(X_train, y_train)
    all_model_objects = {**base_models, tuned_name: tuned_model}
    for name, m_obj in all_model_objects.items():
        if name in all_metrics:
            m_obj.fit(X_train, y_train)

    viz_paths = generate_all_visualizations(
        all_metrics, all_model_objects, feature_names, cv_results
    )

    # -- 5. Results summary -----------------------------------------------
    print("\n[STEP 5/5] Results Summary")
    print_summary(all_metrics, best_name, cv_results)
    print(f"\n  Best model saved -> models/best_model.joblib")
    print(f"  Scaler saved     -> models/scaler.joblib")
    print(f"  Visualizations   -> visualizations/")

    # -- Prediction -------------------------------------------------------
    if interactive:
        interactive_predict(model=best_model, scaler=scaler,
                            feature_names=feature_names)
    else:
        print("\n[DEMO] Running sample prediction ...")
        demo_predict(best_model, scaler, feature_names)

    print("\n[SUCCESS] Pipeline complete.\n")
    return all_metrics, best_model, best_name


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Heart Disease ML Pipeline")
    parser.add_argument(
        "--predict", action="store_true",
        help="Launch interactive prediction prompt after training"
    )
    args = parser.parse_args()
    run_pipeline(interactive=args.predict)
