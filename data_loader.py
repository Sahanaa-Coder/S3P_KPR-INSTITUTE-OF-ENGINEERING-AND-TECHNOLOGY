"""
data_loader.py
--------------
Handles loading, preprocessing, and splitting the Heart Disease dataset.
Uses the UCI Heart Disease dataset fetched via sklearn / ucimlrepo.
Falls back to a synthetic version if unavailable.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------
# Column metadata for the UCI Heart Disease dataset
# ---------------------------------------------------------------------------
FEATURE_NAMES = [
    "age", "sex", "cp", "trestbps", "chol",
    "fbs", "restecg", "thalach", "exang",
    "oldpeak", "slope", "ca", "thal"
]

FEATURE_DESCRIPTIONS = {
    "age":      "Age in years",
    "sex":      "Sex (1 = male; 0 = female)",
    "cp":       "Chest pain type (0-3)",
    "trestbps": "Resting blood pressure (mm Hg)",
    "chol":     "Serum cholesterol (mg/dl)",
    "fbs":      "Fasting blood sugar > 120 mg/dl (1 = true; 0 = false)",
    "restecg":  "Resting ECG results (0-2)",
    "thalach":  "Maximum heart rate achieved",
    "exang":    "Exercise induced angina (1 = yes; 0 = no)",
    "oldpeak":  "ST depression induced by exercise",
    "slope":    "Slope of peak exercise ST segment (0-2)",
    "ca":       "Number of major vessels colored by fluoroscopy (0-3)",
    "thal":     "Thalassemia type (1=normal; 2=fixed defect; 3=reversable defect)",
}

CATEGORICAL_FEATURES = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]
NUMERICAL_FEATURES   = ["age", "trestbps", "chol", "thalach", "oldpeak"]


def load_heart_disease_data() -> pd.DataFrame:
    """
    Load the Heart Disease dataset.

    Tries three sources in order:
      1. Local CSV (data/heart.csv) if already downloaded.
      2. ucimlrepo package (pip install ucimlrepo).
      3. Synthetic dataset generated with realistic distributions.

    Returns
    -------
    pd.DataFrame
        Raw dataframe with features + 'target' column (0 = No Risk, 1 = Risk).
    """
    import os

    if os.path.basename(os.path.dirname(__file__)) == "src":
        local_path = os.path.join(os.path.dirname(__file__), "..", "data", "heart.csv")
    else:
        local_path = os.path.join(os.path.dirname(__file__), "data", "heart.csv")

    # Ensure data directory exists
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    # --- 1. Local file ---
    if os.path.exists(local_path):
        print("[INFO] Loading dataset from local CSV ...")
        df = pd.read_csv(local_path)
        if "target" not in df.columns and "num" in df.columns:
            df["target"] = (df["num"] > 0).astype(int)
        df["target"] = (df["target"] > 0).astype(int)   # binarise
        return df

    # --- 2. ucimlrepo ---
    try:
        from ucimlrepo import fetch_ucirepo
        print("[INFO] Fetching dataset via ucimlrepo ...")
        heart = fetch_ucirepo(id=45)
        X = heart.data.features
        y = heart.data.targets
        df = X.copy()
        df.columns = FEATURE_NAMES
        df["target"] = (y.values.ravel() > 0).astype(int)
        df.to_csv(local_path, index=False)
        print(f"[INFO] Dataset saved to {local_path}")
        return df
    except Exception as e:
        print(f"[WARN] ucimlrepo not available ({e}). Generating synthetic dataset ...")

    # --- 3. Synthetic fallback ---
    return _generate_synthetic_dataset(n=303, seed=42)


def _generate_synthetic_dataset(n: int = 303, seed: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic Heart Disease dataset with realistic distributions.

    Parameters
    ----------
    n    : number of samples
    seed : random seed for reproducibility

    Returns
    -------
    pd.DataFrame
    """
    rng = np.random.default_rng(seed)

    age      = rng.integers(29, 78, n)
    sex      = rng.choice([0, 1], n, p=[0.32, 0.68])
    cp       = rng.choice([0, 1, 2, 3], n, p=[0.47, 0.17, 0.28, 0.08])
    trestbps = rng.normal(131, 17, n).clip(94, 200).astype(int)
    chol     = rng.normal(246, 52, n).clip(126, 564).astype(int)
    fbs      = rng.choice([0, 1], n, p=[0.85, 0.15])
    restecg  = rng.choice([0, 1, 2], n, p=[0.50, 0.48, 0.02])
    thalach  = rng.normal(149, 23, n).clip(71, 202).astype(int)
    exang    = rng.choice([0, 1], n, p=[0.68, 0.32])
    oldpeak  = np.round(rng.exponential(1.0, n).clip(0, 6.2), 1)
    slope    = rng.choice([0, 1, 2], n, p=[0.21, 0.47, 0.32])
    ca       = rng.choice([0, 1, 2, 3], n, p=[0.59, 0.22, 0.12, 0.07])
    thal     = rng.choice([1, 2, 3], n, p=[0.19, 0.55, 0.26])

    # Construct target with a realistic ~46% positive rate
    risk_score = (
        (cp == 0).astype(int) * 2
        + (exang == 1).astype(int)
        + (ca > 0).astype(int)
        + (thal == 3).astype(int)
        + (oldpeak > 2).astype(int)
        - (thalach > 150).astype(int)
    )
    target = (risk_score + rng.normal(0, 1, n) > 1.5).astype(int)

    df = pd.DataFrame({
        "age": age, "sex": sex, "cp": cp,
        "trestbps": trestbps, "chol": chol, "fbs": fbs,
        "restecg": restecg, "thalach": thalach, "exang": exang,
        "oldpeak": oldpeak, "slope": slope, "ca": ca,
        "thal": thal, "target": target
    })

    import os
    if os.path.basename(os.path.dirname(__file__)) == "src":
        local_path = os.path.join(os.path.dirname(__file__), "..", "data", "heart.csv")
    else:
        local_path = os.path.join(os.path.dirname(__file__), "data", "heart.csv")
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    df.to_csv(local_path, index=False)
    print(f"[INFO] Synthetic dataset saved to {local_path}")
    return df


def preprocess_data(df: pd.DataFrame):
    """
    Full preprocessing pipeline: imputation → encoding → scaling → split.

    Parameters
    ----------
    df : raw dataframe (features + 'target' column)

    Returns
    -------
    X_train, X_test, y_train, y_test : numpy arrays
    scaler                            : fitted StandardScaler
    feature_names                     : list of feature column names
    """
    # --- Separate features and target ---
    X = df.drop("target", axis=1).copy()
    y = df["target"].values

    feature_names = list(X.columns)

    # --- Handle missing values ---
    num_imputer = SimpleImputer(strategy="median")
    cat_imputer = SimpleImputer(strategy="most_frequent")

    num_cols = [c for c in NUMERICAL_FEATURES if c in X.columns]
    cat_cols = [c for c in CATEGORICAL_FEATURES if c in X.columns]

    if num_cols:
        X[num_cols] = num_imputer.fit_transform(X[num_cols])
    if cat_cols:
        X[cat_cols] = cat_imputer.fit_transform(X[cat_cols])

    # --- Encode categorical variables (they are already numeric in UCI dataset,
    #     but we one-hot-encode cp, restecg, slope, thal for richer representation) ---
    multi_cat = ["cp", "restecg", "slope", "thal"]
    multi_cat = [c for c in multi_cat if c in X.columns]
    X = pd.get_dummies(X, columns=multi_cat, drop_first=True)

    feature_names = list(X.columns)

    # --- Train-test split (80 : 20, stratified) ---
    X_train, X_test, y_train, y_test = train_test_split(
        X.values, y, test_size=0.20, random_state=42, stratify=y
    )

    # --- Feature scaling ---
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)

    print(f"[INFO] Preprocessing complete -> Train: {X_train.shape}, Test: {X_test.shape}")
    return X_train, X_test, y_train, y_test, scaler, feature_names
