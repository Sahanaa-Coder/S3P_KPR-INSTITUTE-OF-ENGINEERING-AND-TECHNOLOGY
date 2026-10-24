# Atria Twin — AI-Powered Cardiovascular Digital Twin
### Submission-ready README skeleton and working project summary

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9.1-orange?logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Submission%20draft-orange)

---

## Submission metadata (draft only; do not publish until the repo is public)

- Team name: S3P
- College / institution: KPR Institute of Engineering and Technology
- Proposed public repo / folder name: `S3P_KPR_Institute_of_Engineering_and_Technology`
- License: MIT
- Repo status: not yet public; publish only after all required challenge files are present and verified
- Public GitHub publication checklist:
  1. Create the public repo with the exact name above.
  2. Push the verified working branch after all code and docs are complete.
  3. Confirm the README, license, project title, architecture link, presentation link, and demo video are live and reachable.
  4. If a public repo is not yet live, keep links as placeholders and do not claim they are available.

## Challenge requirement checklist

| Requirement | Status | Link or placeholder |
|---|---|---|
| Team details and college details | Draft | Pending public repo publish |
| Project title | Draft | `Atria Twin` |
| Problem statement and healthcare use case | Draft | To be filled in before public release |
| Technical stack | Draft | Python 3.12, Streamlit, Plotly, NumPy, pandas, scikit-learn, pytest |
| AI/ML details | Draft | Synthetic-only digital twin prototype; model and evaluation must be verified before publication |
| Open-source license | Draft | MIT |
| Video link (minimum 20 minutes) | Placeholder | `TBA` |
| Architecture diagram link (PDF/PPT) | Placeholder | `TBA` |
| Presentation link (PDF/PPT) | Placeholder | `TBA` |
| Repo public and accessible | Not yet run | TBA |

---

Atria Twin is a doctor-facing cardiovascular research prototype and multimodal digital twin. It combines static patient/EHR-like context with longitudinal wearable telemetry to estimate the risk of a precisely defined synthetic physiological future-event within a 30-minute forecast horizon.

### Multimodal Future-Event Prediction System
- **Prediction API**: `predict_future_event(patient_context, telemetry_history, patient_baseline, forecast_horizon_minutes=30)` available from `atria_twin.prediction_api`.
- **Target Definition**: Evaluates whether within a 30-minute horizon (sampled at 5-minute intervals), at least two consecutive readings satisfy:
  1. `heart_rate_bpm >= baseline_hr + 18 bpm`
  2. `rmssd_ms <= baseline_rmssd * 0.65`
  3. `systolic_mmhg >= baseline_sbp + 15 mmHg`
- **Leakage-Safe Architecture**: Two-stream pipeline separating static EHR features (`ColumnTransformer` with imputation and encoding) from causal wearable telemetry features (`[t - 30m, t]`). Patient IDs are strictly disjoint between training, validation, and test cohorts.
- **Model Training & Cohort**: 600 synthetic patient profiles with longitudinal trajectories, 70% train (420 patients), 15% validation (90 patients), 15% test (90 patients).
- **Held-Out Evaluation Results (1,800 test windows from 90 held-out patients)**:
  - Multimodal AI Model: **ROC-AUC: 0.9991** | **PR-AUC: 0.9947** | **F1: 0.9751** | **Balanced Acc: 0.9872** | **Precision: 0.9690** | **Recall: 0.9812** | **Specificity: 0.9932** | **Brier Score: 0.0070**
  - Wearable-Only AI Baseline: **ROC-AUC: 0.9990** | **PR-AUC: 0.9940** | **F1: 0.9750**
  - Persistence Baseline: **F1: 0.6842**
- **Artifact Provenance**:
  - `artifacts/multimodal_twin/multimodal_event_model.joblib`
  - `artifacts/multimodal_twin/multimodal_evaluation.json`

The default **Digital Twin** workspace links a selected fictional `DEMO-AT-*` record to a seeded five-minute synthetic telemetry replay, a patient-specific baseline, chronological state updates, a multimodal AI future-event risk forecast with calibrated probability and top contributing evidence, and side-by-side comparison with a rule-based linear extrapolation comparator. All replay and scenario state is isolated by patient in the Streamlit session.


### Windows PowerShell quick start

From the canonical project root, run the dashboard using Python with Streamlit on port 8502:

```powershell
python -m streamlit run atria_twin/app.py --server.port 8502 --browser.gatherUsageStats false
```

Open [http://127.0.0.1:8502/](http://127.0.0.1:8502/).

To run the complete automated test suite:

```powershell
pytest -q tests/
```

### Vercel Serverless Prediction API

The project includes production-ready Vercel serverless functions in [`api/`](./api):
- **Health Check (`GET /api/health`)**: Returns service status, version, and runtime metadata.
- **Multimodal Prediction (`POST /api/predict`, `GET /api/predict`)**:
  - `GET /api/predict`: Returns API contract, schema, and sample payload documentation.
  - `POST /api/predict`: Evaluates longitudinal patient context and telemetry history, returning full risk probability, confidence, risk category, and feature attributions.

### Dashboard workspaces

| Workspace | What it currently shows |
|---|---|
| **Digital Twin** (default) | Selected synthetic patient, deterministic session-isolated telemetry replay, baseline-relative chronological twin state, missingness/freshness, manual session-only telemetry overrides, and a 30-minute patient-linked fixed trend heuristic. Neutral sleep/activity/stress controls compare baseline and scenario outputs side by side. All values and outcomes are synthetic. |
| **Patient Overview** | Inspect the selected synthetic patient's history, diagnoses, medications, labs, BP, wearable observations, provenance and trends; navigate directly to that patient's twin. |
| **Clinical Assessment** | Compact, unvalidated-risk status, grouped record summaries, missing/stale information and a collapsed detailed factor inventory; no probability is computed. |
| **Research & Validation** | Strict LTAFDB validation, acquisition state, Record 30 policy, causal feature gate and model/evaluation evidence, kept separate from fictional records. |
| **Synthetic Clinic · Simulation** | The pre-existing separate fictional HR/RMSSD replay with an illustrative CUSUM; never an AF prediction or clinical alert. |
| **UCI Model + Telemetry** | Separate classifier output for held-out UCI prevalent `num > 0` records and the unlinked illustrative HR/RMSSD replay. |

### Combined-input simulation model and last verified evaluation

| Setting | Implementation |
|---|---|
| Static input | 13 available UCI clinical feature fields, used as unlinked context templates; dataset target and record ID are excluded from features. |
| Dynamic input | Generated HR, RMSSD, systolic/diastolic BP, SpO₂, sleep, daily steps, and stress time series, with seeded sensor dropouts. |
| Observation / forecast | Trailing 30 minutes, sampled each 5 minutes; forecast the next 30 minutes. |
| Target | Two consecutive future samples meet the documented HR/RMSSD/systolic-pressure thresholds relative to the synthetic profile's first-30-minute baseline. |
| Model / split | Median/mode imputation, scaling, one-hot encoding and class-weighted logistic regression; reproducible 300-profile training command, with patient groups and UCI context rows assigned disjointly. |
| Verified runtime v2 run | 300 generated profiles (225 train / 75 holdout), seed `240823`; 1,500 held-out windows (1,274 negative / 226 positive generated labels). The v2 artifact and report in the serving copy were reproduced in the isolated verification environment; see [COPY_COMPARISON.md](COPY_COMPARISON.md). The source-tree combined-model artifact remains v1 and was not replaced. |
| v2 metrics at fixed 0.50 threshold | Accuracy 0.9673; precision 0.8340; recall 0.9779; F1 0.9002; AUROC 0.9864. Confusion matrix, truth rows and predicted columns `[0,1]`: `[[1230,44],[5,221]]`. |

The v2 combined-input model evaluates consistency with generated simulator rules only. It is not a real event predictor, clinical validation, calibration study, or external validation. The source `.venv` remains broken for SciPy; verification used a separate isolated environment. The patient-linked default Digital Twin uses the distinct fixed-rule path described below. The independent UCI `num > 0` classifier is a different prevalent-label task.

The hand-authored patient directory and its simulations remain distinct from the combined model's generated profiles; the patient-facing Clinical Assessment continues to report **clinical risk estimate unavailable**. Patient replay state and manual overrides last only for the Streamlit browser session; reset restores the seeded stream. Scenario controls compare the unmodified baseline to the same patient-linked pipeline after documented illustrative adjustments. The existing main-timeline Reset to Baseline control resets its widgets through a callback before rerender. See [patient twin workflow and limitations](docs/PATIENT_TWIN_WORKFLOW.md).

For the repeatable 24-minute presenter-led walkthrough, see [docs/SUMMIT_DEMO_SCRIPT.md](docs/SUMMIT_DEMO_SCRIPT.md) and the [recording checklist](deliverables/DEMO_RECORDING_CHECKLIST.md). The final narrated video is not yet recorded.

### Repository map

```text
atria_twin/       Streamlit app, UCI model, synthetic patient records/fusion, simulation, and gated LTAFDB research workflow
artifacts/        Research-readiness reports and reproducible static-model outputs
deliverables/     Architecture PDF/PPTX and summit presentation PDF/PPTX
docs/             Status, demo script, slide outline, and editable architecture source
tests/            Python unittest suite
tools/            Reproducible slide generation and PowerPoint PDF export helpers
work/             Local source data and resumable acquisition state; not complete research waveforms
```

The app's current navigation workspaces and truthful summit walkthrough are described in the [24-minute demo script](docs/SUMMIT_DEMO_SCRIPT.md). For the editable architecture source and status of existing exports, see [the architecture diagram](docs/architecture.mmd) and [architecture notes](docs/ARCHITECTURE.md). The generated deck is a visual companion, not a direct Mermaid render. Test passes indicate software behavior only; they are not clinical evidence.

### Patient-linked replay and evaluation

The patient-linked replay/forecast implementation is versioned separately as `patient-linked-synthetic-trend-v1.1`; it does not overwrite the previous combined-input v1/v2 models. It uses a 30-minute trailing window of seven timestamped readings sampled every five minutes, then linearly projects HR, RMSSD, and systolic BP over the next 30 minutes. The synthetic target is positive when at least two consecutive future 5-minute readings exceed the patient's recorded synthetic baseline by HR +18 bpm, RMSSD at or below 65% of baseline, and systolic BP +15 mmHg. This is a generated anomaly rule, not a clinical event.

Replay controls are patient/session-scoped: start/resume, pause, step, reset, and 1x/2x/4x playback. Baseline is held at the latest synthetic EHR-like wearable/BP record and is not updated from replay, so generated deviations cannot contaminate it. Forecast input uses only observations at or before the current replay cursor; the forecast is unavailable with an incomplete/gapped 30-minute window or insufficient valid readings for key sensors. Scenario changes are explicit illustrative perturbations, not causal medical effects. Streamlit session state persists through reruns, but not through a new browser session or server restart.

Reproduce the grouped synthetic rule evaluation in the isolated project environment:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python -m atria_twin.evaluate_patient_twin --episodes-per-patient 100 --seed 20261023
```

The command writes once to `artifacts/patient_twin_forecast_v1_1/evaluation.json` and refuses to overwrite a non-matching report. This fixed rule has no fitting/training split; its evaluation is grouped by three hand-authored synthetic patient templates and compares against a last-reading persistence baseline. Its metrics are simulator agreement only; three templates do not support population generalization, and no confidence interval or calibrated probability is reported. For the evidence and current challenge gaps, see [CHALLENGE_COMPLIANCE_AUDIT.md](CHALLENGE_COMPLIANCE_AUDIT.md).

### Dataset provenance and use

The AF research source is the PhysioNet Long Term AF Database (LTAFDB), version 1.0.0. Stage 12 records the official version-specific page's ODC Attribution License v1.0 designation and required citation/annotation acknowledgements. The currently approved cohort is limited to the five records above; execution was attempted and stopped incomplete. No new transfers are performed as part of this package. The separate cross-sectional classifier uses the local UCI `heart_disease_uci.csv` and its existing `num` labels. All code, source-data and research-use conditions must be reviewed before publication or redistribution.

**Software licence:** project code is licensed under the [MIT License](LICENSE), selected by the owner. This does not relicense UCI or PhysioNet datasets, legacy assets, or third-party dependencies; review their separate terms before redistribution.

**Ethical and clinical-use notice:** the UCI classifier reproduces a prevalent dataset label and is not a patient-specific/future risk model. Patient profiles and simulated telemetry are fictional, not clinical observations. The project is not clinically validated and must not be used for diagnosis, screening, triage, treatment, or care decisions.

---

## 📌 Project Overview

This project builds an end-to-end **Machine Learning pipeline** to predict heart disease risk from patient clinical data. It was developed as a portfolio project during the **Thiranex AI Internship**.

The pipeline covers the full ML lifecycle:
- Automated data loading (UCI Heart Disease dataset or synthetic fallback)
- Preprocessing with imputation, encoding, and scaling
- Exploratory Data Analysis with rich visualizations
- Training and comparing 4 models (Logistic Regression, Decision Tree, Random Forest, Tuned RF)
- GridSearchCV hyperparameter tuning + 5-fold cross-validation
- Automatic best model selection and persistence
- Interactive prediction CLI with confidence scores

---

## 📁 Project Structure

```
heart_disease_ml/
├── data/
│   └── heart.csv                    # Dataset (auto-generated if absent)
├── src/
│   ├── __init__.py
│   ├── data_loader.py               # Data loading & preprocessing pipeline
│   ├── eda.py                       # EDA: stats, plots, distributions
│   ├── model_trainer.py             # Model definitions, training, evaluation
│   ├── visualizer.py                # All evaluation visualizations
│   └── predictor.py                 # Inference module (CLI + programmatic)
├── models/
│   ├── best_model.joblib            # Serialised best model
│   ├── scaler.joblib                # Fitted StandardScaler
│   └── feature_names.joblib         # Encoded feature list
├── notebooks/
│   └── heart_disease_analysis.ipynb # Full walkthrough notebook
├── visualizations/
│   ├── 01_class_balance.png
│   ├── 02_correlation_heatmap.png
│   ├── 03_feature_distributions.png
│   ├── 04_categorical_counts.png
│   ├── 05_confusion_matrices.png
│   ├── 06_roc_curves.png
│   ├── 07_feature_importance.png
│   ├── 08_metrics_comparison.png
│   └── 09_cross_validation.png
├── main.py                          # Pipeline entry point
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/heart-disease-ml.git
cd heart-disease-ml

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

**requirements.txt**
```
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
joblib>=1.3.0
```

---

## 🚀 Usage

### Run the full pipeline
```bash
python main.py
```
This will:
1. Load / generate the dataset → `data/heart.csv`
2. Run EDA and save visualizations → `visualizations/`
3. Train all 4 models and evaluate them
4. Tune Random Forest with GridSearchCV
5. Save the best model → `models/best_model.joblib`
6. Run a demo prediction on a sample patient

### Interactive prediction
```bash
python main.py --predict
```
Prompts for each clinical feature and returns:
- Prediction label: **RISK** or **NO RISK**
- Confidence score (%)
- Full probability breakdown

### Use predictor programmatically
```python
import joblib
from src.predictor import predict

model         = joblib.load("models/best_model.joblib")
scaler        = joblib.load("models/scaler.joblib")
feature_names = joblib.load("models/feature_names.joblib")

patient = {
    "age": 62, "sex": 1, "cp": 0,
    "trestbps": 150, "chol": 260, "fbs": 1,
    "restecg": 1, "thalach": 130, "exang": 1,
    "oldpeak": 3.2, "slope": 2, "ca": 2, "thal": 3
}

result = predict(patient, model, scaler, feature_names)
print(result["label"])        # ⚠️  RISK — Heart Disease Likely
print(result["confidence"])   # 0.913
```

### Jupyter notebook
```bash
cd notebooks
jupyter notebook heart_disease_analysis.ipynb
```

---

## 📊 Dataset

**Source:** UCI Heart Disease Dataset (Cleveland subset, 303 patients, 13 features)

| Feature    | Description                                      |
|------------|--------------------------------------------------|
| `age`      | Age in years                                     |
| `sex`      | Sex (1 = Male, 0 = Female)                       |
| `cp`       | Chest pain type (1–4 in the checked-in CSV)           |
| `trestbps` | Resting blood pressure (mm Hg)                   |
| `chol`     | Serum cholesterol (mg/dl)                        |
| `fbs`      | Fasting blood sugar > 120 mg/dl (1 = True)       |
| `restecg`  | Resting ECG results (0–2)                        |
| `thalach`  | Maximum heart rate achieved                      |
| `exang`    | Exercise-induced angina (1 = Yes)                |
| `oldpeak`  | ST depression induced by exercise                |
| `slope`    | Slope of peak exercise ST segment (1–3 in the checked-in CSV) |
| `ca`       | Number of major vessels coloured by fluoroscopy  |
| `thal`     | Thalassemia code (3, 6, or 7 in the checked-in CSV)   |
| `target`   | **0 = absent, 1 = present heart disease** (binarised) |

---

## 🤖 Models & Results

| Model                    | Accuracy | Precision | Recall | F1     | ROC-AUC |
|--------------------------|----------|-----------|--------|--------|---------|
| Logistic Regression      | 0.8525   | 0.8387    | 0.8667 | 0.8525 | 0.9054  |
| Decision Tree            | 0.7705   | 0.8333    | 0.6667 | 0.7407 | 0.8027  |
| Random Forest            | 0.8197   | 0.8519    | 0.7667 | 0.8070 | 0.8624  |
| Random Forest (Tuned)    | 0.7705   | 0.8077    | 0.7000 | 0.7500 | 0.8753  |

**Best model: Logistic Regression** (F1 = 0.8525, AUC = 0.9054)

### GridSearchCV — Best Hyperparameters (Random Forest)
```
n_estimators     : 200
max_depth        : 10
min_samples_split: 2
min_samples_leaf : 2
```

### 5-Fold Cross-Validation

| Model                 | CV Accuracy       | CV F1             |
|-----------------------|-------------------|-------------------|
| Logistic Regression   | 0.7809 ± 0.0290   | 0.7609 ± 0.0549   |
| Decision Tree         | 0.6491 ± 0.0991   | 0.6513 ± 0.0920   |
| Random Forest         | 0.7316 ± 0.0459   | 0.7219 ± 0.0437   |
| Random Forest (Tuned) | 0.7605 ± 0.0432   | 0.7511 ± 0.0368   |

---

## 🖼️ Visualizations

| File                          | Description                                         |
|-------------------------------|-----------------------------------------------------|
| `01_class_balance.png`        | Bar chart of target class distribution              |
| `02_correlation_heatmap.png`  | Lower-triangle feature correlation heatmap          |
| `03_feature_distributions.png`| KDE + histogram for numerical features by target    |
| `04_categorical_counts.png`   | Count plots for key categorical features by target  |
| `05_confusion_matrices.png`   | Confusion matrices for all 4 models                 |
| `06_roc_curves.png`           | Overlaid ROC curves with AUC scores                 |
| `07_feature_importance.png`   | Top-15 feature importances (Decision Tree + RF)     |
| `08_metrics_comparison.png`   | Grouped bar chart: Accuracy/Precision/Recall/F1/AUC |
| `09_cross_validation.png`     | 5-fold CV accuracy & F1 with error bars             |

---

## 🔧 Future Improvements

1. **Real UCI data** — plug in `ucimlrepo` or download `heart.csv` directly from the UCI repository for authentic results
2. **XGBoost / LightGBM** — gradient-boosting models typically outperform RF on tabular medical data
3. **SHAP explainability** — use SHAP values for per-prediction feature-level explanations (important for clinical trust)
4. **Class-imbalance handling** — apply SMOTE or class-weight adjustments for skewed datasets
5. **Flask / FastAPI REST API** — expose the predictor as a web service
6. **Streamlit dashboard** — interactive web app for clinicians to enter values and see risk scores
7. **Threshold tuning** — optimise the classification threshold for Recall (sensitivity) over Accuracy, given the medical context
8. **Multilingual support** — add Indian-language descriptions in the prediction CLI

---

## 👤 Author

**Sahanaa**
Thiranex AI Internship — 2026
[GitHub](https://github.com/Sahanaa-Coder) · [LinkedIn](https://www.linkedin.com/in/sahanaa-mr-61782a36b)
---
