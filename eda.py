"""
eda.py
------
Exploratory Data Analysis: summary statistics, distributions,
correlation heatmap, and class balance plot.
All figures are saved to the visualizations/ directory.
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

warnings.filterwarnings("ignore")

if os.path.basename(os.path.dirname(__file__)) == "src":
    VIZ_DIR = os.path.join(os.path.dirname(__file__), "..", "visualizations")
else:
    VIZ_DIR = os.path.join(os.path.dirname(__file__), "visualizations")

# ---------------------------------------------------------------------------
# Colour palette (medical / clinical feel)
# ---------------------------------------------------------------------------
PRIMARY   = "#E63946"   # heart red
SECONDARY = "#457B9D"   # steel blue
ACCENT    = "#2EC4B6"   # teal
BG        = "#F8F9FA"
DARK      = "#1D3557"


def _save(fig, name: str):
    os.makedirs(VIZ_DIR, exist_ok=True)
    path = os.path.join(VIZ_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[SAVED] {path}")
    return path


def summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Print and return descriptive statistics.

    Parameters
    ----------
    df : raw dataframe

    Returns
    -------
    pd.DataFrame of summary statistics
    """
    stats = df.describe().T
    stats["missing"] = df.isnull().sum()
    stats["missing_%"] = (df.isnull().mean() * 100).round(2)
    print("\n========== SUMMARY STATISTICS ==========")
    print(stats.to_string())
    print("\n[Class Distribution]")
    vc = df["target"].value_counts()
    print(f"  No Risk (0): {vc.get(0, 0)}  |  Risk (1): {vc.get(1, 0)}")
    return stats


def plot_class_balance(df: pd.DataFrame) -> str:
    """Bar chart showing class balance."""
    fig, ax = plt.subplots(figsize=(6, 4), facecolor=BG)
    counts = df["target"].value_counts().sort_index()
    labels = ["No Risk (0)", "Risk (1)"]
    colors = [SECONDARY, PRIMARY]
    bars = ax.bar(labels, counts.values, color=colors, width=0.5, edgecolor="white", linewidth=1.5)

    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{val}\n({val/len(df)*100:.1f}%)", ha="center", va="bottom",
                fontsize=11, fontweight="bold", color=DARK)

    ax.set_title("Class Balance — Heart Disease Dataset", fontsize=14, fontweight="bold", color=DARK, pad=14)
    ax.set_ylabel("Number of Patients", fontsize=11, color=DARK)
    ax.set_facecolor(BG)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(colors=DARK)
    fig.tight_layout()
    return _save(fig, "01_class_balance.png")


def plot_correlation_heatmap(df: pd.DataFrame) -> str:
    """Correlation heatmap for all numerical features."""
    fig, ax = plt.subplots(figsize=(10, 8), facecolor=BG)
    corr = df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    sns.heatmap(corr, mask=mask, cmap=cmap, center=0, annot=True,
                fmt=".2f", linewidths=0.5, ax=ax,
                annot_kws={"size": 8}, cbar_kws={"shrink": 0.8})
    ax.set_title("Feature Correlation Heatmap", fontsize=14, fontweight="bold", color=DARK, pad=14)
    ax.tick_params(colors=DARK, labelsize=9)
    fig.tight_layout()
    return _save(fig, "02_correlation_heatmap.png")


def plot_feature_distributions(df: pd.DataFrame) -> str:
    """Distribution plots (histogram + KDE) for numerical features split by target."""
    num_cols = ["age", "trestbps", "chol", "thalach", "oldpeak"]
    num_cols = [c for c in num_cols if c in df.columns]

    fig, axes = plt.subplots(2, 3, figsize=(16, 9), facecolor=BG)
    axes = axes.flatten()

    for i, col in enumerate(num_cols):
        ax = axes[i]
        for val, color, label in [(0, SECONDARY, "No Risk"), (1, PRIMARY, "Risk")]:
            subset = df[df["target"] == val][col].dropna()
            ax.hist(subset, bins=20, alpha=0.5, color=color, label=label, density=True)
            subset.plot.kde(ax=ax, color=color, linewidth=2)
        ax.set_title(col.upper(), fontsize=11, fontweight="bold", color=DARK)
        ax.set_facecolor(BG)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(fontsize=9)
        ax.tick_params(colors=DARK, labelsize=8)

    # Hide unused subplot
    for j in range(len(num_cols), len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("Feature Distributions by Heart Disease Risk",
                 fontsize=15, fontweight="bold", color=DARK, y=1.01)
    fig.tight_layout()
    return _save(fig, "03_feature_distributions.png")


def plot_categorical_counts(df: pd.DataFrame) -> str:
    """Count plots for key categorical features."""
    cat_cols = ["sex", "cp", "fbs", "exang"]
    cat_cols = [c for c in cat_cols if c in df.columns]
    labels_map = {
        "sex":   {0: "Female", 1: "Male"},
        "cp":    {0: "Typical", 1: "Atypical", 2: "Non-anginal", 3: "Asymptomatic"},
        "fbs":   {0: "≤120 mg/dl", 1: ">120 mg/dl"},
        "exang": {0: "No", 1: "Yes"},
    }

    fig, axes = plt.subplots(1, len(cat_cols), figsize=(16, 5), facecolor=BG)

    for ax, col in zip(axes, cat_cols):
        tmp = df.copy()
        if col in labels_map:
            tmp[col] = tmp[col].map(labels_map[col]).fillna(tmp[col])

        groups = tmp.groupby([col, "target"]).size().unstack(fill_value=0)
        groups.plot(kind="bar", ax=ax, color=[SECONDARY, PRIMARY], edgecolor="white",
                    linewidth=1, rot=15, legend=(col == cat_cols[0]))

        ax.set_title(col.upper(), fontsize=11, fontweight="bold", color=DARK)
        ax.set_facecolor(BG)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(colors=DARK, labelsize=8)
        ax.set_xlabel("")

    if axes[0].get_legend():
        axes[0].legend(["No Risk", "Risk"], fontsize=9)

    fig.suptitle("Categorical Feature Counts by Heart Disease Risk",
                 fontsize=14, fontweight="bold", color=DARK)
    fig.tight_layout()
    return _save(fig, "04_categorical_counts.png")


def run_eda(df: pd.DataFrame):
    """
    Run the full EDA pipeline and save all visualizations.

    Parameters
    ----------
    df : raw dataframe

    Returns
    -------
    dict of saved file paths
    """
    print("\n========== EXPLORATORY DATA ANALYSIS ==========")
    stats = summary_statistics(df)
    paths = {
        "class_balance":    plot_class_balance(df),
        "correlation":      plot_correlation_heatmap(df),
        "distributions":    plot_feature_distributions(df),
        "categorical":      plot_categorical_counts(df),
    }
    print("\n[EDA] All visualizations saved.")
    return paths
