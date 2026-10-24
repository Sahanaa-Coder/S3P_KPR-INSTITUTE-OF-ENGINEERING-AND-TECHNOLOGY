"""
visualizer.py
-------------
Generates and saves all model evaluation plots:
  - Confusion matrices
  - ROC curve comparison
  - Feature importance (tree-based models)
  - Model metrics comparison bar chart
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

if os.path.basename(os.path.dirname(__file__)) == "src":
    VIZ_DIR = os.path.join(os.path.dirname(__file__), "..", "visualizations")
else:
    VIZ_DIR = os.path.join(os.path.dirname(__file__), "visualizations")

# Palette
PRIMARY   = "#E63946"
SECONDARY = "#457B9D"
ACCENT    = "#2EC4B6"
GOLD      = "#F4A261"
BG        = "#F8F9FA"
DARK      = "#1D3557"
PALETTE   = [PRIMARY, SECONDARY, ACCENT, GOLD]


def _save(fig, name: str) -> str:
    os.makedirs(VIZ_DIR, exist_ok=True)
    path = os.path.join(VIZ_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[SAVED] {path}")
    return path


# ---------------------------------------------------------------------------
# Confusion matrices
# ---------------------------------------------------------------------------

def plot_confusion_matrices(all_metrics: dict) -> str:
    """
    Plot confusion matrix for every model in a single figure.

    Parameters
    ----------
    all_metrics : dict returned by model_trainer.train_all_models

    Returns
    -------
    str : saved file path
    """
    n = len(all_metrics)
    ncols = min(n, 2)
    nrows = (n + 1) // 2
    fig, axes = plt.subplots(nrows, ncols, figsize=(7 * ncols, 5.5 * nrows),
                             facecolor=BG)
    axes = np.array(axes).flatten()

    for ax, (name, m) in zip(axes, all_metrics.items()):
        cm = m["cm"]
        sns.heatmap(
            cm, annot=True, fmt="d", ax=ax,
            cmap=sns.light_palette(SECONDARY, as_cmap=True),
            linewidths=2, linecolor="white",
            xticklabels=["No Risk", "Risk"],
            yticklabels=["No Risk", "Risk"],
            annot_kws={"size": 14, "weight": "bold"},
        )
        ax.set_title(name, fontsize=12, fontweight="bold", color=DARK, pad=10)
        ax.set_xlabel("Predicted", fontsize=10, color=DARK)
        ax.set_ylabel("Actual", fontsize=10, color=DARK)
        ax.tick_params(colors=DARK, labelsize=9)

    for ax in axes[n:]:
        ax.set_visible(False)

    fig.suptitle("Confusion Matrices — All Models",
                 fontsize=15, fontweight="bold", color=DARK, y=1.01)
    fig.tight_layout()
    return _save(fig, "05_confusion_matrices.png")


# ---------------------------------------------------------------------------
# ROC curves
# ---------------------------------------------------------------------------

def plot_roc_curves(all_metrics: dict) -> str:
    """
    Overlay ROC curves for all models that provide probability estimates.

    Parameters
    ----------
    all_metrics : dict returned by model_trainer.train_all_models

    Returns
    -------
    str : saved file path
    """
    fig, ax = plt.subplots(figsize=(8, 6), facecolor=BG)
    ax.set_facecolor(BG)

    for (name, m), color in zip(all_metrics.items(), PALETTE):
        if "fpr" not in m:
            continue
        auc = m["roc_auc"]
        ax.plot(m["fpr"], m["tpr"], color=color, linewidth=2.2,
                label=f"{name}  (AUC = {auc:.3f})")

    ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random Classifier")
    ax.fill_between([0, 1], [0, 1], alpha=0.05, color="grey")

    ax.set_title("ROC Curve Comparison", fontsize=14, fontweight="bold", color=DARK, pad=12)
    ax.set_xlabel("False Positive Rate", fontsize=11, color=DARK)
    ax.set_ylabel("True Positive Rate", fontsize=11, color=DARK)
    ax.legend(fontsize=9, framealpha=0.8, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(colors=DARK)
    fig.tight_layout()
    return _save(fig, "06_roc_curves.png")


# ---------------------------------------------------------------------------
# Feature importance
# ---------------------------------------------------------------------------

def plot_feature_importance(all_metrics: dict, models_dict: dict,
                            feature_names: list) -> str:
    """
    Bar chart of feature importances for tree-based models.

    Parameters
    ----------
    all_metrics   : dict returned by model_trainer.train_all_models
    models_dict   : dict[name, fitted model]  (passed explicitly)
    feature_names : list of feature column names

    Returns
    -------
    str : saved file path
    """
    tree_models = {n: m for n, m in models_dict.items()
                   if hasattr(m, "feature_importances_")}
    if not tree_models:
        return ""

    n = len(tree_models)
    fig, axes = plt.subplots(1, n, figsize=(9 * n, 7), facecolor=BG)
    axes = np.array([axes]).flatten() if n == 1 else np.array(axes).flatten()

    for ax, (name, model) in zip(axes, tree_models.items()):
        imps = model.feature_importances_
        idx  = np.argsort(imps)[::-1][:15]        # top 15
        top_names  = [feature_names[i] for i in idx]
        top_imps   = imps[idx]

        colors = [PRIMARY if i == 0 else SECONDARY for i in range(len(top_names))]
        ax.barh(range(len(top_names))[::-1], top_imps, color=colors,
                edgecolor="white", linewidth=0.8)
        ax.set_yticks(range(len(top_names))[::-1])
        ax.set_yticklabels(top_names, fontsize=9)
        ax.set_title(f"Feature Importance\n{name}", fontsize=12,
                     fontweight="bold", color=DARK, pad=10)
        ax.set_xlabel("Importance Score", fontsize=10, color=DARK)
        ax.set_facecolor(BG)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(colors=DARK, labelsize=8)

    fig.suptitle("Feature Importance — Tree-Based Models",
                 fontsize=14, fontweight="bold", color=DARK)
    fig.tight_layout()
    return _save(fig, "07_feature_importance.png")


# ---------------------------------------------------------------------------
# Metrics comparison
# ---------------------------------------------------------------------------

def plot_metrics_comparison(all_metrics: dict) -> str:
    """
    Grouped bar chart comparing Accuracy, Precision, Recall, F1, ROC-AUC
    across all models.

    Parameters
    ----------
    all_metrics : dict returned by model_trainer.train_all_models

    Returns
    -------
    str : saved file path
    """
    metric_keys = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    metric_labels = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]

    names  = list(all_metrics.keys())
    data   = {k: [all_metrics[n][k] for n in names] for k in metric_keys}

    x      = np.arange(len(metric_keys))
    width  = 0.18
    n_mod  = len(names)
    offsets = np.linspace(-(n_mod - 1) / 2 * width, (n_mod - 1) / 2 * width, n_mod)

    fig, ax = plt.subplots(figsize=(13, 6), facecolor=BG)
    ax.set_facecolor(BG)

    for i, (name, offset) in enumerate(zip(names, offsets)):
        vals = [data[k][i] for k in metric_keys]
        bars = ax.bar(x + offset, vals, width, label=name,
                      color=PALETTE[i % len(PALETTE)],
                      edgecolor="white", linewidth=0.8)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                    f"{v:.2f}", ha="center", va="bottom", fontsize=7, color=DARK)

    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels, fontsize=11, color=DARK)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Score", fontsize=11, color=DARK)
    ax.set_title("Model Performance Comparison", fontsize=14,
                 fontweight="bold", color=DARK, pad=12)
    ax.legend(fontsize=9, framealpha=0.8, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(colors=DARK)
    fig.tight_layout()
    return _save(fig, "08_metrics_comparison.png")


# ---------------------------------------------------------------------------
# Cross-validation results
# ---------------------------------------------------------------------------

def plot_cv_results(cv_results: dict) -> str:
    """
    Bar chart with error bars showing 5-fold CV accuracy and F1.

    Parameters
    ----------
    cv_results : dict returned by model_trainer.train_all_models

    Returns
    -------
    str : saved file path
    """
    names    = list(cv_results.keys())
    acc_m    = [cv_results[n]["cv_acc_mean"] for n in names]
    acc_s    = [cv_results[n]["cv_acc_std"]  for n in names]
    f1_m     = [cv_results[n]["cv_f1_mean"]  for n in names]
    f1_s     = [cv_results[n]["cv_f1_std"]   for n in names]

    x      = np.arange(len(names))
    width  = 0.35

    fig, ax = plt.subplots(figsize=(11, 5), facecolor=BG)
    ax.set_facecolor(BG)
    ax.bar(x - width / 2, acc_m, width, yerr=acc_s, label="Accuracy",
           color=SECONDARY, capsize=5, edgecolor="white")
    ax.bar(x + width / 2, f1_m,  width, yerr=f1_s,  label="F1 Score",
           color=PRIMARY,   capsize=5, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=9, color=DARK, rotation=10)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Score", fontsize=11, color=DARK)
    ax.set_title("5-Fold Cross-Validation Results", fontsize=14,
                 fontweight="bold", color=DARK, pad=12)
    ax.legend(fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(colors=DARK)
    fig.tight_layout()
    return _save(fig, "09_cross_validation.png")


# ---------------------------------------------------------------------------
# Master runner
# ---------------------------------------------------------------------------

def generate_all_visualizations(all_metrics: dict, models_dict: dict,
                                 feature_names: list, cv_results: dict) -> dict:
    """
    Generate and save all model evaluation visualizations.

    Parameters
    ----------
    all_metrics   : from model_trainer.train_all_models
    models_dict   : dict[name, fitted model]
    feature_names : list of feature names
    cv_results    : from model_trainer.train_all_models

    Returns
    -------
    dict of saved file paths
    """
    print("\n========== GENERATING VISUALIZATIONS ==========")
    paths = {
        "confusion_matrices":  plot_confusion_matrices(all_metrics),
        "roc_curves":          plot_roc_curves(all_metrics),
        "feature_importance":  plot_feature_importance(all_metrics, models_dict, feature_names),
        "metrics_comparison":  plot_metrics_comparison(all_metrics),
        "cv_results":          plot_cv_results(cv_results),
    }
    print("[VIZ] All model visualizations saved.")
    return paths
