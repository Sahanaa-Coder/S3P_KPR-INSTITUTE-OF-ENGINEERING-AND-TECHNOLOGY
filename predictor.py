"""
predictor.py
------------
Prediction module: loads the saved best model and scaler,
accepts user input features, and outputs:
  - Prediction label (Risk / No Risk)
  - Confidence score (probability)
"""

import os
import joblib
import numpy as np
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = _PROJECT_DIR

FEATURE_DESCRIPTIONS = {
    "age":      ("Age in years", int, (20, 100)),
    "sex":      ("Sex — 1=Male, 0=Female", int, (0, 1)),
    "cp":       ("Chest pain type — 0=Typical, 1=Atypical, 2=Non-anginal, 3=Asymptomatic", int, (0, 3)),
    "trestbps": ("Resting blood pressure (mm Hg)", int, (80, 220)),
    "chol":     ("Serum cholesterol (mg/dl)", int, (100, 600)),
    "fbs":      ("Fasting blood sugar >120 mg/dl — 1=True, 0=False", int, (0, 1)),
    "restecg":  ("Resting ECG — 0=Normal, 1=ST-T abnormality, 2=LV hypertrophy", int, (0, 2)),
    "thalach":  ("Maximum heart rate achieved", int, (60, 220)),
    "exang":    ("Exercise induced angina — 1=Yes, 0=No", int, (0, 1)),
    "oldpeak":  ("ST depression induced by exercise", float, (0.0, 7.0)),
    "slope":    ("Slope of peak exercise ST segment — 0=Upsloping, 1=Flat, 2=Downsloping", int, (0, 2)),
    "ca":       ("Number of major vessels coloured by fluoroscopy (0-3)", int, (0, 3)),
    "thal":     ("Thalassemia — 1=Normal, 2=Fixed defect, 3=Reversable defect", int, (1, 3)),
}

# Sample patient for demo / testing
SAMPLE_PATIENT = {
    "age": 55, "sex": 1, "cp": 0,
    "trestbps": 140, "chol": 250, "fbs": 0,
    "restecg": 1, "thalach": 145, "exang": 1,
    "oldpeak": 2.3, "slope": 2, "ca": 0, "thal": 2,
}


def load_artifacts(scaler=None):
    """
    Load the saved best model. Optionally accept a scaler passed in memory.

    Parameters
    ----------
    scaler : fitted StandardScaler (optional; loaded from disk if None)

    Returns
    -------
    (model, scaler)
    """
    model_path  = os.path.join(MODELS_DIR, "best_model.joblib")
    scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"No saved model found at {model_path}. "
            "Run main.py first to train and save the model."
        )

    model = joblib.load(model_path)

    if scaler is None:
        if os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
        else:
            scaler = None   # caller must handle

    return model, scaler


def preprocess_input(raw_features: dict, scaler, feature_names: list) -> np.ndarray:
    """
    Convert a raw feature dict into the scaled input vector expected by the model.

    Parameters
    ----------
    raw_features  : dict of {feature_name: value}
    scaler        : fitted StandardScaler
    feature_names : list of column names (after one-hot encoding)

    Returns
    -------
    np.ndarray of shape (1, n_features)
    """
    import pandas as pd
    from sklearn.preprocessing import StandardScaler as _SS

    # Build a single-row DataFrame
    base_cols = list(FEATURE_DESCRIPTIONS.keys())
    df = pd.DataFrame([{c: raw_features.get(c, 0) for c in base_cols}])

    # One-hot encode the same columns as during training
    multi_cat = ["cp", "restecg", "slope", "thal"]
    df = pd.get_dummies(df, columns=multi_cat, drop_first=True)

    # Align columns to training feature set
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0
    df = df[[c for c in feature_names if c in df.columns]]

    # Pad if needed
    x = df.values.astype(float)
    if scaler is not None:
        # scaler may have been fit on different number of features if alignment differs
        try:
            x = scaler.transform(x)
        except Exception:
            pass    # proceed unscaled — edge case

    return x


def predict(raw_features: dict, model, scaler, feature_names: list) -> dict:
    """
    Run inference on a single patient's features.

    Parameters
    ----------
    raw_features  : dict of {feature_name: raw_value}
    model         : fitted estimator
    scaler        : fitted StandardScaler
    feature_names : list of column names after one-hot encoding

    Returns
    -------
    dict with 'label', 'prediction', 'confidence', 'probabilities'
    """
    x = preprocess_input(raw_features, scaler, feature_names)
    pred   = model.predict(x)[0]
    prob   = model.predict_proba(x)[0] if hasattr(model, "predict_proba") else None

    label      = "[WARNING] RISK - Heart Disease Likely" if pred == 1 else "[OK] NO RISK - Heart Disease Unlikely"
    confidence = float(np.max(prob)) if prob is not None else None

    return {
        "prediction":    int(pred),
        "label":         label,
        "confidence":    confidence,
        "probabilities": {"No Risk": float(prob[0]), "Risk": float(prob[1])} if prob is not None else None,
    }


def interactive_predict(model=None, scaler=None, feature_names: list = None):
    """
    CLI interface: prompts the user for each feature, runs prediction,
    and prints the result.

    Parameters
    ----------
    model, scaler, feature_names : optional pre-loaded artifacts
    """
    if model is None:
        model, scaler = load_artifacts(scaler)

    if feature_names is None:
        feature_names = list(FEATURE_DESCRIPTIONS.keys())

    print("\n" + "=" * 55)
    print("   Heart Disease Risk Predictor — Enter Patient Data")
    print("=" * 55)
    print("Press Enter to use the default sample value.\n")

    raw = {}
    defaults = SAMPLE_PATIENT

    for feat, (desc, dtype, (lo, hi)) in FEATURE_DESCRIPTIONS.items():
        default_val = defaults.get(feat, "")
        while True:
            prompt = f"{feat} [{desc}] (default={default_val}): "
            user_in = input(prompt).strip()
            if user_in == "":
                raw[feat] = dtype(default_val)
                break
            try:
                val = dtype(user_in)
                if not (lo <= val <= hi):
                    print(f"  [!] Value should be between {lo} and {hi}. Try again.")
                    continue
                raw[feat] = val
                break
            except ValueError:
                print(f"  [!] Expected {dtype.__name__}. Try again.")

    result = predict(raw, model, scaler, feature_names)
    _print_result(result, raw)
    return result


def demo_predict(model, scaler, feature_names: list) -> dict:
    """
    Run a demo prediction on the built-in SAMPLE_PATIENT without user input.

    Parameters
    ----------
    model, scaler, feature_names : pre-loaded artifacts

    Returns
    -------
    dict prediction result
    """
    result = predict(SAMPLE_PATIENT, model, scaler, feature_names)
    _print_result(result, SAMPLE_PATIENT)
    return result


def _print_result(result: dict, features: dict):
    print("\n" + "=" * 55)
    print("  INPUT FEATURES")
    print("=" * 55)
    for k, v in features.items():
        print(f"  {k:12s}: {v}")
    print("\n" + "=" * 55)
    print("  PREDICTION RESULT")
    print("=" * 55)
    print(f"  {result['label']}")
    if result["confidence"] is not None:
        print(f"  Confidence : {result['confidence'] * 100:.1f}%")
    if result["probabilities"] is not None:
        p = result["probabilities"]
        print(f"  P(No Risk) : {p['No Risk'] * 100:.1f}%")
        print(f"  P(Risk)    : {p['Risk'] * 100:.1f}%")
    print("=" * 55 + "\n")
