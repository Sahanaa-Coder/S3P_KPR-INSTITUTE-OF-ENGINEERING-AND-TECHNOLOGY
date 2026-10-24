import os
import sys
import joblib
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure the project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from predictor import predict, MODELS_DIR, FEATURE_DESCRIPTIONS

# Set Page Config
st.set_page_config(
    page_title="Heart Disease Risk Classification",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
<style>
    .main {
        background-color: #fdfdfd;
    }
    .main-title {
        font-family: 'Outfit', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #1D3557;
        margin-bottom: 0.1rem;
    }
    .subtitle {
        font-family: 'Outfit', sans-serif;
        font-size: 1.2rem;
        color: #457B9D;
        margin-bottom: 2rem;
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1D3557;
        border-bottom: 2px solid #E63946;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        margin-bottom: 1rem;
    }
    .risk-alert {
        padding: 1.5rem;
        border-radius: 12px;
        background-color: #FFE3E3;
        border-left: 6px solid #E63946;
        color: #8C0000;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 1.5rem;
    }
    .norisk-alert {
        padding: 1.5rem;
        border-radius: 12px;
        background-color: #E6F7F5;
        border-left: 6px solid #2EC4B6;
        color: #005F55;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Load artifacts
@st.cache_resource
def load_all_artifacts():
    model_path = os.path.join(MODELS_DIR, "best_model.joblib")
    scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")
    feature_names_path = os.path.join(MODELS_DIR, "feature_names.joblib")
    
    # Train if models are missing
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        st.warning("Model files missing. Running the training pipeline first...")
        from main import run_pipeline
        run_pipeline(interactive=False)
        
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    feature_names = joblib.load(feature_names_path)
    return model, scaler, feature_names

try:
    model, scaler, feature_names = load_all_artifacts()
except Exception as e:
    st.error(f"Error loading model artifacts: {e}")
    st.stop()

# Header
col1, col2 = st.columns([1, 12])
with col1:
    st.markdown("<div style='font-size: 4rem; padding-top: 1rem;'>🫀</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='main-title'>Clinical Heart Disease Classifier</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Predictive Modeling Using Machine Learning | Risk Assessment Dashboard</div>", unsafe_allow_html=True)

# Tabs
tab_calc, tab_triage, tab_model, tab_eda = st.tabs([
    "📋 Patient Risk Calculator",
    "🏥 Clinic Triage",
    "🤖 Model Info & Performance",
    "📊 EDA & Insights",
])

# -------------------------------------------------------------
# TAB 1: Calculator
# -------------------------------------------------------------
with tab_calc:
    st.markdown("<div class='section-title'>Patient Health Information</div>", unsafe_allow_html=True)
    
    col_input, col_result = st.columns([2, 3])
    
    with col_input:
        with st.form("patient_form"):
            st.write("📝 **Enter Patient Attributes**")
            
            # Demographics
            c1, c2 = st.columns(2)
            with c1:
                age = st.slider("Age (years)", 20, 100, 55)
            with c2:
                sex = st.radio("Sex", ["Female", "Male"], index=1)
                
            # Chest pain & clinical values
            c3, c4 = st.columns(2)
            with c3:
                cp = st.selectbox("Chest Pain Type", [
                    "0: Typical Angina",
                    "1: Atypical Angina",
                    "2: Non-anginal Pain",
                    "3: Asymptomatic"
                ], index=0)
            with c4:
                trestbps = st.slider("Resting Blood Pressure (mmHg)", 80, 220, 130)
                
            c5, c6 = st.columns(2)
            with c5:
                chol = st.slider("Serum Cholesterol (mg/dl)", 100, 600, 240)
            with c6:
                fbs = st.radio("Fasting Blood Sugar > 120 mg/dl", ["False", "True"], index=0)
                
            # ECG & Stress Test
            c7, c8 = st.columns(2)
            with c7:
                restecg = st.selectbox("Resting ECG Results", [
                    "0: Normal",
                    "1: ST-T wave abnormality",
                    "2: Left ventricular hypertrophy"
                ], index=0)
            with c8:
                thalach = st.slider("Max Heart Rate Achieved (bpm)", 60, 220, 150)
                
            c9, c10 = st.columns(2)
            with c9:
                exang = st.radio("Exercise-Induced Angina", ["No", "Yes"], index=0)
            with c10:
                oldpeak = st.slider("ST Depression (oldpeak)", 0.0, 7.0, 1.0, step=0.1)
                
            c11, c12 = st.columns(2)
            with c11:
                slope = st.selectbox("Slope of Peak Exercise ST", [
                    "0: Upsloping",
                    "1: Flat",
                    "2: Downsloping"
                ], index=1)
            with c12:
                ca = st.slider("Number of Major Vessels (ca)", 0, 3, 0)
                
            thal = st.selectbox("Thalassemia Status", [
                "1: Normal Thalassemia",
                "2: Fixed Defect",
                "3: Reversible Defect"
            ], index=1)
            
            submit_btn = st.form_submit_button("Calculate Heart Disease Risk", use_container_width=True)
            
    with col_result:
        st.markdown("<div class='section-title'>Diagnostic Results</div>", unsafe_allow_html=True)

        if submit_btn:
            # Prepare inputs
            patient_data = {
                "age": age,
                "sex": 1 if sex == "Male" else 0,
                "cp": int(cp.split(":")[0]),
                "trestbps": trestbps,
                "chol": chol,
                "fbs": 1 if fbs == "True" else 0,
                "restecg": int(restecg.split(":")[0]),
                "thalach": thalach,
                "exang": 1 if exang == "Yes" else 0,
                "oldpeak": oldpeak,
                "slope": int(slope.split(":")[0]),
                "ca": ca,
                "thal": int(thal.split(":")[0])
            }
            
            res = predict(patient_data, model, scaler, feature_names)
            is_risk = res["prediction"] == 1
            confidence = res.get("confidence")
            probabilities = res.get("probabilities")
            
            if is_risk:
                st.markdown(f"""
                <div class='risk-alert'>
                    ⚠️ RISK DETECTED — Patient exhibits clinical risk of Heart Disease
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='norisk-alert'>
                    ✅ NO RISK DETECTED — Patient appears to be at low risk
                </div>
                """, unsafe_allow_html=True)
                
            # Display Confidence
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            if confidence is not None:
                st.write(f"### Classification Confidence: **{confidence * 100:.1f}%**")
                st.progress(confidence)
            else:
                st.write("### Classification Confidence: **N/A**")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Probabilities
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.write("#### Probability Breakdown")
            if probabilities is not None:
                prob_df = pd.DataFrame({
                    "Classification": ["Low Risk", "High Risk"],
                    "Probability": [probabilities.get("No Risk", 0.0), probabilities.get("Risk", 0.0)]
                })
                fig, ax = plt.subplots(figsize=(6, 2), facecolor="#ffffff")
                colors = ["#2EC4B6", "#E63946"]
                bars = ax.barh(prob_df["Classification"], prob_df["Probability"], color=colors, height=0.5)
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width + 0.02, bar.get_y() + bar.get_height() / 2,
                            f'{width * 100:.1f}%', va='center', ha='left', fontsize=10, fontweight='bold')
                ax.set_xlim(0, 1.15)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_color('#cccccc')
                ax.tick_params(left=True, bottom=False, labelbottom=False)
                st.pyplot(fig)
            else:
                st.write("Probability breakdown is unavailable for this model.")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Complete the form and press 'Calculate Heart Disease Risk' to see the prediction.")

        # Health indicators
        st.write("🩺 **Clinical Guidelines Reference:**")
        st.markdown(f"""
        - **Blood Pressure:** {trestbps} mmHg (Normal: < 120 mmHg) - *{'Elevated' if trestbps >= 130 else 'Normal/Acceptable'}*
        - **Cholesterol:** {chol} mg/dl (Normal: < 200 mg/dl) - *{'High' if chol >= 240 else ('Borderline' if chol >= 200 else 'Desirable')}*
        - **Max Heart Rate:** {thalach} bpm (Estimated max: {220 - age} bpm)
        """)

# -------------------------------------------------------------
# TAB 2: Multi-patient clinic triage
# -------------------------------------------------------------
with tab_triage:
    st.markdown("<div class='section-title'>Multi-Patient Clinic Triage</div>", unsafe_allow_html=True)
    st.write(
        "Upload a CSV with one patient per row and the same clinical fields used by the "
        "individual calculator. The existing model will score each row and rank the "
        "patients by its predicted risk probability."
    )
    feature_cols = list(FEATURE_DESCRIPTIONS)
    st.caption("Required columns: " + ", ".join(feature_cols) + ". Optional identifier column: patient_id or name.")
    uploaded_patients = st.file_uploader("Upload patient CSV", type=["csv"], key="triage_csv")

    if uploaded_patients is not None:
        try:
            patients_df = pd.read_csv(uploaded_patients)
            missing_cols = [column for column in feature_cols if column not in patients_df.columns]
            if patients_df.empty:
                st.error("The uploaded CSV has no patient rows.")
            elif missing_cols:
                st.error("Missing required columns: " + ", ".join(missing_cols))
            else:
                id_col = next((col for col in ("patient_id", "name") if col in patients_df.columns), None)
                numeric_df = patients_df[feature_cols].apply(pd.to_numeric, errors="coerce")
                invalid_rows = numeric_df.isna().any(axis=1)
                for column, (_, dtype, (low, high)) in FEATURE_DESCRIPTIONS.items():
                    invalid_rows |= (numeric_df[column] < low) | (numeric_df[column] > high)
                    if dtype is int:
                        invalid_rows |= numeric_df[column] % 1 != 0

                if invalid_rows.any():
                    bad_rows = ", ".join(str(index + 2) for index in patients_df.index[invalid_rows][:10])
                    suffix = " …" if int(invalid_rows.sum()) > 10 else ""
                    st.error(
                        f"Invalid or out-of-range values found on CSV row(s): {bad_rows}{suffix}. "
                        "Check that all required feature values are numeric and within their expected ranges."
                    )
                else:
                    results = []
                    for row_index, row in numeric_df.iterrows():
                        raw_patient = {
                            column: FEATURE_DESCRIPTIONS[column][1](row[column])
                            for column in feature_cols
                        }
                        prediction = predict(raw_patient, model, scaler, feature_names)
                        probabilities = prediction.get("probabilities") or {}
                        results.append({
                            "Patient": patients_df.at[row_index, id_col] if id_col else f"Patient {row_index + 1}",
                            "Model result": "Risk predicted" if prediction["prediction"] == 1 else "No risk predicted",
                            "Risk probability (%)": round(probabilities.get("Risk", float("nan")) * 100, 1),
                            "Confidence (%)": round(prediction["confidence"] * 100, 1)
                            if prediction.get("confidence") is not None else None,
                        })

                    results_df = pd.DataFrame(results).sort_values(
                        "Risk probability (%)", ascending=False, na_position="last"
                    ).reset_index(drop=True)
                    risk_count = int((results_df["Model result"] == "Risk predicted").sum())
                    metric_cols = st.columns(3)
                    metric_cols[0].metric("Patients scored", len(results_df))
                    metric_cols[1].metric("Risk predicted", risk_count)
                    metric_cols[2].metric("No risk predicted", len(results_df) - risk_count)
                    st.dataframe(results_df, width="stretch", hide_index=True)
                    st.download_button(
                        "Download triage results",
                        data=results_df.to_csv(index=False).encode("utf-8"),
                        file_name="thiranex_clinic_triage.csv",
                        mime="text/csv",
                    )
                    st.caption(
                        "This is a model-based prioritization aid using the project's current classifier. "
                        "It is not a diagnosis or a substitute for clinician assessment."
                    )
        except (pd.errors.ParserError, UnicodeDecodeError) as exc:
            st.error(f"Could not read the uploaded CSV: {exc}")
        except Exception as exc:
            st.error(f"Triage scoring failed: {exc}")

# -------------------------------------------------------------
# TAB 3: Model Performance
# -------------------------------------------------------------
with tab_model:
    st.markdown("<div class='section-title'>Machine Learning Model Performance</div>", unsafe_allow_html=True)
    st.write("We compared four classification models. Below is the performance achieved on the UCI Heart Disease test set:")
    
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.write("### Model Metrics Comparison")
        metrics_data = {
            "Model": ["Logistic Regression", "Decision Tree", "Random Forest", "Random Forest (Tuned)"],
            "Accuracy": [0.8525, 0.7705, 0.8197, 0.9180],
            "Precision": [0.8387, 0.8333, 0.8519, 0.8710],
            "Recall": [0.8667, 0.6667, 0.7667, 0.9643],
            "F1-Score": [0.8525, 0.7407, 0.8070, 0.9153],
            "ROC-AUC": [0.9054, 0.8027, 0.8624, 0.9567]
        }
        st.table(pd.DataFrame(metrics_data).set_index("Model"))
        st.markdown("**Best Selected Model:** `Random Forest (Tuned)` which exhibits the highest recall (sensitivity) and F1-Score, crucial for clinical diagnostic workflows.")
        
    with m_col2:
        st.write("### Visualizations")
        viz_option = st.selectbox("Select Evaluation Plot to View", [
            "Metrics Comparison",
            "Confusion Matrices",
            "ROC Curves",
            "Feature Importance"
        ])
        
        viz_map = {
            "Metrics Comparison": "08_metrics_comparison.png",
            "Confusion Matrices": "05_confusion_matrices.png",
            "ROC Curves": "06_roc_curves.png",
            "Feature Importance": "07_feature_importance.png"
        }
        
        viz_file_name = viz_map[viz_option]
        viz_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), viz_file_name)
        if os.path.exists(viz_path):
            st.image(viz_path, use_column_width=True)
        else:
            st.info("Run the training pipeline or check that main.py was run to generate visualizations.")

# -------------------------------------------------------------
# TAB 4: Dataset Insights (EDA)
# -------------------------------------------------------------
with tab_eda:
    st.markdown("<div class='section-title'>Exploratory Data Analysis & Insights</div>", unsafe_allow_html=True)
    st.write("Below are the insights generated from the UCI Heart Disease Cleveland dataset:")
    
    eda_col1, eda_col2 = st.columns([2, 3])
    with eda_col1:
        st.write("### Key Correlations & Distributions")
        st.markdown("""
        * **Class Balance**: The dataset features an approximately balanced target distribution (~54% No Risk, ~46% Risk), ensuring models aren't biased toward a single category.
        * **Major Predictors**: Chest Pain (`cp`), Thalassemia type (`thal`), and number of major vessels (`ca`) show strong positive correlation with disease risk.
        * **Max Heart Rate (`thalach`)**: Shows negative correlation with risk; patients achieving higher heart rates during stress tests generally exhibit a lower risk profile.
        """)
        
        # Dataset stats summary
        local_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "heart.csv")
        if not os.path.exists(local_csv):
            local_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "heart.csv")
        if os.path.exists(local_csv):
            df = pd.read_csv(local_csv)
            st.write("### Dataset Quick Stats")
            st.dataframe(df.describe().T[["count", "mean", "min", "max"]])
        else:
            st.info("Dataset CSV not found. It will be downloaded or generated when running predictions.")
            
    with eda_col2:
        eda_viz = st.selectbox("Select EDA Visualization", [
            "Class Balance",
            "Correlation Heatmap",
            "Numerical Features Distributions",
            "Categorical Features Counts"
        ])
        
        eda_map = {
            "Class Balance": "01_class_balance.png",
            "Correlation Heatmap": "02_correlation_heatmap.png",
            "Numerical Features Distributions": "03_feature_distributions.png",
            "Categorical Features Counts": "04_categorical_counts.png"
        }
        
        eda_file_name = eda_map[eda_viz]
        eda_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), eda_file_name)
        if os.path.exists(eda_path):
            st.image(eda_path, use_column_width=True)
        else:
            st.info("EDA visualizations will be displayed here once generated.")
