# Source and Running Dashboard Copy Comparison

Audit date: 2026-10-23. The original copy comparison was read-only. A subsequent Phase 2 implementation updated source code and added new versioned synthetic evaluation/documentation; no existing dataset, v1/v2 model artifact, static-model artifact, LTAFDB file, or live runtime copy was changed.

## Locations and active process

| Role | Exact path |
|---|---|
| Authoritative nested source tree | `<PROJECT_ROOT>` |
| Runtime dashboard copy | `<TEMP_DIR>/atria_twin_dashboard_6730286a` |
| Short-path junction used for source environment commands | `<TEMP_DIR>/atria_twin_project_6730286a` (junction to source; not a distinct project copy) |

`Get-NetTCPConnection -State Listen -LocalPort 8501,8502` showed port 8501 bound to `127.0.0.1`, PID 4404. Its command is:

```text
"<PYTHON_EXECUTABLE>" -m streamlit run <TEMP_DIR>\atria_twin_dashboard_6730286a\atria_twin\app.py --server.headless true --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

Parent PID 26248 was launched as:

```text
"<TEMP_DIR>\atria_twin_project_6730286a\.venv\Scripts\python.exe" -m streamlit run <TEMP_DIR>\atria_twin_dashboard_6730286a\atria_twin\app.py --server.headless true --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

`http://127.0.0.1:8501/_stcore/health` returned **200 / `ok`**; `/` returned **200**. Port 8502 returned a connection error. HTTP health confirms the server is responsive; it does not prove the saved model loaded or a prediction was made.

## File-set and SHA-256 comparison

At the original comparison snapshot, the source and runtime copies contained **39 / 39 identical files under `atria_twin/`** (all SHA-256 values equal), **87 / 87 corresponding files under `artifacts/`** (83 equal, four different), and both datasets were byte-identical. This is a historical baseline; Phase 2 subsequently added and changed source files, which are not present in the serving snapshot.

| File | Source SHA-256 | Runtime SHA-256 | Finding |
|---|---|---|---|
| `heart.csv` | `2c47d9ee8b2e0d30e81c113a079baec0bb3814b1cef093e675610de45df54ffc` | `2c47d9ee8b2e0d30e81c113a079baec0bb3814b1cef093e675610de45df54ffc` | Identical |
| `heart_disease_uci.csv` | `574f2fa2b43012fa25fca4fcdb36bd7c6bccdd0af4242f6c0e4c8633c5a072ae` | `574f2fa2b43012fa25fca4fcdb36bd7c6bccdd0af4242f6c0e4c8633c5a072ae` | Identical; also the dataset hash in both forecast evaluation reports |
| `atria_twin/app.py` | `6c9bd947e5df7c53aaad000fe308ce2ab5792f03a9f147b020c14d628d9c2f4f` | Same | Identical |
| `atria_twin/simulated_forecast.py` | `9f6293203c5ec8bf263621bc2bfb9e979c2557cd6e8a78f113db45705c063473` | Same | Identical; source declares model v2 |
| `atria_twin/forecast_dashboard.py` | `1d6861d8fa664b36cc9529113179b7460dc7d9d02b9e20dc9f542e24184be53d` | Same | Identical |
| `atria_twin/static_model.py` | `2c7b323282cd9c973f4db78211b5cb820a1429dfd088ac5a86047ba6f479a036` | Same | Identical |
| `artifacts/simulated_forecast/simulated_forecast_model.joblib` | `7d49b26aa58adeabef03ddd708652cef6a36bf5e77083507521fafc0d688f634` | `0e6527b7745373b9fc360d440adf52048e361a73a049495d8fe5589561f84ee0` | Different: source 17,310 bytes; runtime 928,005 bytes |
| `artifacts/simulated_forecast/simulated_forecast_evaluation.json` | `a6031601d24e7b9704487b0e567a0984152c0604cc57e7111751df5644bfd69c` | `66afb2866dd84e14c5702260ac38fd7d809b32bb1ef7154497fdaf032693ce78` | Different; only top-level difference is `model_version` (v1 vs v2) |
| `artifacts/static_model/uci_heart_logistic.joblib` | `d5ff2d5c2b8297a30dae61e8ec52d8fe41bf8ea0879d4576bb2a6646a17e8de8` | `627857fa11915947c87ca9426e219942b862b18926cea37e3b59badd7a4d14bb` | Different; source 6,538 bytes; runtime 6,554 bytes |
| `artifacts/static_model/uci_heart_evaluation.json` | `7fead2b0e187ea9f6bc349badcd88db75b84d3656fa6fff8ac0874bb856db60f` | `461eb9150309dc23aee8b9c53d40623848b39235663208705be035c83ff44afb` | Different; holdout metrics match except Brier score differs at approximately 1.4e-14 |

The source `requirements.txt` SHA-256 is `43fb2a9c8b0e38d3fd770702925172bf99658e098b9c0c675b6787c69aae2f27`; it is absent from the runtime copy. The runtime copy also has no `tests/`, `docs/`, `tools/`, or `.streamlit/` directory. The source likewise has no `.streamlit/` directory. Thus the runtime copy is a serving snapshot, not a full project clone.

## Initial forecast artifact status before isolated verification

Both evaluation JSON files report the same task rule: at least two consecutive future five-minute samples within a 30-minute horizon exceed a generated HR/blood-pressure threshold and cross a generated RMSSD threshold. Both record a 30-minute observation window, 30-minute horizon, five-minute sampling, training seed `240823`, train/test seed `42`, 225 training and 75 holdout profiles, 4,500 training windows, and 1,500 holdout windows. The data SHA-256 matches the bundled `heart_disease_uci.csv`.

The current source defines 37 raw inputs: 13 UCI clinical context fields plus 24 temporal statistics (mean, slope/minute, latest) from eight synthetic wearable columns. `train_simulated_forecast_model` generates 300 fictional profiles, makes patient-grouped and UCI-context splits, and writes both the serialized pipeline and evaluation JSON when given an artifact directory. The report labels this as simulation-only; `clinical_validation` and `real_event_prediction` are false. The v2 report records accuracy 0.9673, precision 0.8340, recall 0.9779, F1 0.9002, and ROC-AUC 0.9864 on its synthetic holdout. These are stored report values, not independently recalculated results in this audit.

At this initial comparison point, the v2 process was reproducible in principle from source/data, but the source venv's missing SciPy module prevented model loading or prediction. This status was resolved **only in the separate verification environment** described below; the source environment and dashboard were not repaired or altered. The web health check alone is not prediction evidence.

## Test and dependency checks

Executed against the source project's Python 3.12.10 environment; no packages were installed or changed:

```text
$source = '<PROJECT_ROOT>'
$python = Join-Path $source '.venv\Scripts\python.exe'
& $python --version
Python 3.12.10

& $python -m pytest --collect-only -q
No module named pytest

& $python -m pytest -q
No module named pytest
```

The environment metadata reports NumPy 2.5.4, pandas 3.1.0, scikit-learn 1.9.1, SciPy 1.18.1, joblib 1.6.0, and Streamlit 1.66.1; pytest is not installed. Importing scikit-learn (and thus the model module) fails with:

```text
ModuleNotFoundError: No module named 'scipy.optimize._trustregion_constr.minimize_trustregion_constr'
```

The static and forecast serialized artifacts could not be freshly loaded in this environment. No prediction was newly verified. The HTTP-served dashboard remains running; no restart or interaction that could retrain/save an artifact was performed.

Other executed checks and results:

| Command/check | Result |
|---|---|
| `Get-NetTCPConnection -State Listen -LocalPort 8501,8502` plus `Get-CimInstance Win32_Process` for listener/parent PIDs | 8501: PID 4404, parent 26248, serving the runtime path above. 8502: no listener. |
| `Invoke-WebRequest http://127.0.0.1:8501/_stcore/health` and `/` | HTTP 200 (`ok`) and HTTP 200. |
| `Invoke-WebRequest http://127.0.0.1:8502/_stcore/health` | Connection failed. |
| `Get-FileHash -Algorithm SHA256` and a recursive Python SHA-256 comparison over matching `atria_twin/` and `artifacts/` files | 39 package files: all identical. 87 artifacts: 83 identical, four different, no missing/extra files. |
| SHA-256 checks of `heart.csv` and `heart_disease_uci.csv` in both roots | Both datasets match byte-for-byte; hashes are in the table above. |
| Source-venv package-version metadata query | Versions reported above; pytest package metadata absent. |
| Read-only `joblib.load`/forecast-run validation attempt against runtime v2 artifact | Failed during scikit-learn/SciPy import; no model object was loaded and no prediction was produced. |

## Follow-up verification in an isolated environment (2026-10-23)

### SciPy diagnosis and isolated environment

The source environment reports Python 3.12.10, NumPy 2.5.4, pandas 3.1.0, scikit-learn 1.9.1, SciPy 1.18.1, and joblib 1.6.0. `python -m pip check` returned `No broken requirements found`; this checks declared version constraints only. The installed `scipy-1.18.1.dist-info/RECORD` lists `scipy/optimize/_trustregion_constr/minimize_trustregion_constr.py` with expected size 27,165 bytes and a SHA-256 digest, but that file is absent in the source venv. Importing scikit-learn fails because SciPy imports this missing module. This is an incomplete/corrupt package file set, not a reported dependency-version conflict. No repair was attempted in the source environment.

Created this separate environment, outside both project trees:

```powershell
$verify = Join-Path $env:TEMP 'atria_twin_verify_20261023'
python -m venv $verify
$python = Join-Path $verify 'Scripts\python.exe'
& $python -m pip install 'numpy==2.5.4' 'pandas==3.1.0' 'scikit-learn==1.9.1' 'scipy==1.18.1' 'matplotlib==3.11.2' 'seaborn==0.13.2' 'joblib==1.6.0' 'streamlit==1.66.1' 'plotly==7.1.0' 'wfdb==4.3.1' 'python-pptx==1.0.2' 'pytest==8.4.2'
```

Those pins match the source environment's installed project dependency versions; pytest was added for validation. The installation succeeded, `pip check` passed, and imports of SciPy's missing module, NumPy, pandas, scikit-learn, joblib, and pytest succeeded in the isolated environment. This restored module presence only in the new environment; source environment and server were untouched.

### Runtime forecast v2: artifact inspection, inference, and reproduction

Read-only loading of the runtime artifact verified:

- Artifact and evaluation `model_version`: `simulated-cardiovascular-anomaly-logistic-v2`.
- Exactly 37 raw model input columns: five numeric UCI context columns, eight categorical UCI context columns, and 24 temporal features (mean, slope per minute, latest for each of eight simulated wearable channels). The serialized pipeline's `feature_names_in_` exactly matches the source model feature schema.
- Dataset SHA-256 `574f2fa2b43012fa25fca4fcdb36bd7c6bccdd0af4242f6c0e4c8633c5a072ae`; training seed `240823`; train/test split seed `42`; 225 training and 75 holdout fictional patient profiles; 4,500 training windows; 1,500 holdout windows.
- Training procedure: shuffle/split UCI context rows using `train_test_split(test_size=0.25, random_state=42)`, generate 300 fictional wearable profiles, hold out 25% of patient groups, extract the 30-minute history features, fit the preprocessing/logistic-regression pipeline, and evaluate on holdout profiles. The output event rule uses future synthetic readings, not observed clinical outcomes.
- Observation window 30 minutes, forecast horizon 30 minutes, five-minute synthetic sampling. The report explicitly sets `clinical_validation: false` and `real_event_prediction: false`.
- Saved synthetic holdout metrics: accuracy `0.9673333333333334`, precision `0.8339622641509434`, recall `0.9778761061946902`, F1 `0.90020366598778`, ROC-AUC `0.9864478126172185`, confusion matrix `[[1230,44],[5,221]]`.

Using the first saved holdout profile with `predict_profile` (no model/artifact writes) produced:

```json
{
  "simulated_anomaly_probability": 0.8876831339726011,
  "predicted_simulated_anomaly": true,
  "model_version": "simulated-cardiovascular-anomaly-logistic-v2",
  "forecast_horizon_minutes": 30,
  "prediction_time": "2026-01-01T05:55:00+00:00",
  "observation_window_start": "2026-01-01T05:25:00+00:00",
  "observation_window_end": "2026-01-01T05:55:00+00:00",
  "input_feature_count": 37,
  "top_model_contributions": [
    ["wearable_temporal__heart_rate_bpm_mean", 1.7045243902383707],
    ["wearable_temporal__rmssd_ms_mean", 1.5333087138361512],
    ["wearable_temporal__systolic_mmhg_mean", 1.2809456170021196],
    ["clinical_numeric__trestbps", 1.0117242242319202],
    ["wearable_temporal__systolic_mmhg_latest", 0.7236765136971051]
  ]
}
```

The probability was finite and within `[0,1]`; all 37 input keys matched the model schema, and the output fields matched the `ForecastOutput` dataclass. The status/provenance fields identify the result as **simulation only**, with UCI context unlinked to the fictional wearable profile. This verifies functioning inference for the synthetic target only; it is not a real future cardiovascular-event prediction.

### Isolated deterministic reproduction

Ran `train_simulated_forecast_model` with the bundled UCI CSV, 300 profiles, and the saved training seed, writing only to a fresh `%TEMP%\atria_twin_repro_20261023_<random-id>\simulated_forecast\` directory. The reproduced evaluation JSON and in-memory evaluation summary matched the saved runtime v2 report exactly, including every metric and split/provenance field. Across all 1,500 holdout windows, the reproduced model's class predictions were identical and the maximum absolute difference between probabilities was `0.0`.

### Separate static classifier check

Loaded and evaluated the separate `artifacts/static_model/uci_heart_logistic.joblib` against the UCI prevalent label `num > 0`. Fresh in-memory `train_static_model` evaluation matched the runtime evaluation report exactly; holdout probabilities matched with maximum absolute difference `0.0`. Saved metrics were accuracy `0.842391304347826`, balanced accuracy `0.8387135341941655`, precision `0.8476190476190476`, recall `0.8725490196078431`, average precision `0.9223401140901656`, ROC-AUC `0.9102104256336682`, and Brier score `0.11909367160648776`. One deterministic holdout example was UCI record 515: predicted prevalent-disease class `0`, probability `0.42512449264837704`, observed label `1`. This is a cross-sectional classifier example, not a forecast.

### Automated tests

An initial repository-root pytest collection attempt failed because pytest recursively collected the historical `backups/stage18_pre_upgrade/tests/test_atria_twin.py`, colliding with the current `tests/test_atria_twin.py` module name. No file hashes changed. The corrected command explicitly selected the current top-level test directory, disabled pytest's cache provider, used importlib mode to avoid same-basename collisions, and disabled bytecode writes:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
& $python -m pytest -p no:cacheprovider --import-mode=importlib -q tests\test_atria_twin.py tests\test_data_readiness.py tests\test_ltafdb_validation.py tests\test_patient_workflow.py tests\test_runtime_dependencies.py tests\test_simulated_forecast.py tests\test_simulation_engine.py tests\test_stage4_safeguards.py tests\test_static_model.py tests\test_waveform_acquisition.py
```

Result: **152 passed, 2 warnings in 10.35 seconds**. Both warnings are WFDB 4.3.1 `Pandas4Warning`s about the deprecated pandas `inplace` argument; no test failed. `pytest.main` also compared SHA-256 for all 364 pre-existing non-environment/non-cache project files before and after its first (collection-error) attempt; there were no changed project hashes. The final test run also used `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`.

### Source/LTAFDB strict validation

The isolated environment ran the validator in memory without an output path:

```python
validate_ltafdb(Path("work/ltafdb_annotations"), require_waveforms=False)
```

Result: **invalid**; acquisition provenance is `verified`, all 84 catalog/header/annotation pairs were inspected, 83 records were valid and one (record `30`) was invalid, with zero complete waveform files. Record 30 has 31,190 annotation entries; annotation 31,190 is at sample `4,198,064`, beyond the header's declared 2,826,240 samples at 128 Hz. Its note is `\x01 Aux`, not an AF rhythm marker according to the project parser. The strict validator correctly returns the error and does not write a report. See the LTAFDB classifications in `CLEANUP_PLAN.md`.

### LTAFDB file inventory, dependencies, and label lineage

Inspected the local source data and derived-evidence paths:

| Path/file group | Count/content | Dependency and classification |
|---|---|---|
| `work/ltafdb_annotations/RECORDS` | Catalog of 84 IDs: `00, 01, 03, 05, 06, 07, 08, 10, 100–105, 11, 110–122, 12, 13, 15–26, 28, 30, 32–35, 37–39, 42–45, 47–49, 51, 53–56, 58, 60, 62, 64–65, 68–72, 74–75, 200–208` (as listed in file order). | Retain; consumed by provenance and validator code. |
| `work/ltafdb_annotations/<ID>.hea` and `<ID>.atr` | 84 headers + 84 reference annotation files. | Retain raw source data. Local hashes match the acquisition manifest. All 168 raw files have distinct SHA-256 values in this tree; no exact raw-file duplicate was found. |
| `work/ltafdb_annotations/acquisition_manifest.json`, `waveform_manifest.json` | Source/license/citation/acknowledgment and local file-integrity metadata; waveform acquisition state `in_progress`. | Retain provenance and resumability state. Manifest provenance is verified locally; its hashes are not signed upstream checksums. |
| `05.dat.part`, `05.dat.part.json`; `110.dat.part`, `110.dat.part.json` | Two incomplete waveform downloads, respectively 41,943,040 / 44,820,480 bytes and 42,991,616 / 43,929,600 bytes; sidecars record chunk hashes. No complete `.dat` files exist. | Retain as resumable partial evidence, not disposable temporary files. |
| `artifacts/data_audit/audit_summary.json`, `decision_windows.csv`, `input_validation.json`, and the three record-30 diagnostic/follow-up/semantics documents plus clarification-request document | Prior annotation-derived counts/windows and validation/issue history. No processed ECG feature table, AF model, AF predictions, or current AF evaluation file exists. | Retain; `audit_summary.json` and `decision_windows.csv` are historical, not current strict-validation/model evidence. |
| `artifacts/research_readiness/stage*/**` | 76 stage reports/evidence files, including stage 8 `eligible_cohort.json`, and distinct stage 13/14 validation and pilot report snapshots. | Retain as historical decision/provenance evidence. A candidate waveform-acquisition cohort is not a complete clinical cohort or model evaluation. |
| LTAFDB-relevant current code and tests | `atria_twin/{download_annotations,download_waveforms,validate_ltafdb,diagnose_record,select_cohort,cohort,labels,audit_dataset,build_features,features,modeling,data_gate,data_readiness,evidence_status,app}.py`; `tests/test_ltafdb_validation.py`, `test_waveform_acquisition.py`, `test_stage4_safeguards.py`, `test_data_readiness.py`, and LTAFDB cases in `test_atria_twin.py`. | Retain; these are active validation/acquisition/gating or test surfaces. The passing tests exercise software/fixtures, not independent clinical adjudication. |
| LTAFDB-related documentation | `atria_twin/DATA_FEASIBILITY.md`, `atria_twin/README.md`, `atria_twin/MODEL_CARD.md`, root `README.md`, `docs/RESEARCH_STATUS_AND_LIMITATIONS.md`, `docs/PATIENT_TWIN_WORKFLOW.md`, `docs/SUMMIT_DEMO_SCRIPT.md`, `docs/SUMMIT_PRESENTATION_OUTLINE.md`, and readiness-stage reports. | Retain; documents explicitly state the limitations and closed gates. |

A SHA-256 scan of **258 files** under `work/ltafdb_annotations/`, `artifacts/data_audit/`, and `artifacts/research_readiness/` found one exact duplicate group: `artifacts/data_audit/input_validation.json` and `artifacts/research_readiness/stage14/full_catalog_validation.json`, digest `a6397a21af824d0e6af805f1a3e8f24d37e7ae825fab8bd11eca931b0fbd7108`. Their stage-specific paths have separate audit value; retain both pending provenance/reference review. No other exact duplicate was found in those scanned paths. Stage 13/14 report files with similar names/sizes are not byte-identical.

The `.atr` annotations are source-provided reference rhythm annotations, but project-level binary AF outcomes are **derived** by `atria_twin/labels.py` from annotated rhythm transitions plus coded duration/lookback/lead-time/horizon rules. The project validates local manifest consistency, WFDB readability, metadata, and sample bounds; this is not independent clinical adjudication or a clinical ground-truth review. `decision_windows.csv` and the saved audit counts are derived labels. The historical summary reports 7,316 AF intervals, 76 unique eligible onset times, 312 positive windows, and 12,957 negative windows; it predates current strict rejection of record 30 and is not a valid current performance result. The AF research path remains blocked by record-30 validation, absent full ECG waveforms, and unverified XQRS temporal causality. The v2 simulated forecast is separate and consumes no LTAFDB data.

## Final audit decision

The v2 artifact is loadable, usable, and deterministically reproducible in the isolated environment. It yields valid output for the generated **simulation-defined** anomaly only. The static UCI model independently reproduces its prevalent-disease classification. The LTAFDB pipeline remains blocked by strict record-30 validation, no complete `.dat` signals, and the documented unverified causal feature gate; no LTAFDB-derived model or valid AF performance evaluation is established. The working dashboard on port 8501 remained healthy. No cleanup, source environment repair, artifact replacement, dataset change, server restart, or security-setting change was performed.

## Decision

The runtime snapshot remains the **verified v2 candidate for the older combined-input simulated-forecast experiment**: its artifact loads, its saved evaluation is exactly reproduced, and its probabilities match the isolated reproduction on all 1,500 holdout windows. The source tree's corresponding combined-model artifact/report remain v1, separate from the new patient-linked rule path (`patient-linked-synthetic-trend-v1.1`) and evaluation in `artifacts/patient_twin_forecast_v1_1/`. The source virtual environment still has a missing SciPy module; tests passed only in the isolated environment. LTAFDB validation remains invalid for record 30, with no complete waveform files and no verified AF model/evaluation. Neither forecast nor static results are clinical validation. The port-8501 runtime copy and all prior artifacts remain unchanged; reconcile/promote only after separate approval and the backup/rollback procedure in `CLEANUP_PLAN.md`.

### Record 30 explicit validation-subset check (2026-10-24)

Using the isolated verification environment and `validate_ltafdb(..., require_waveforms=False)` with no output file:

| Validation call | Result |
|---|---|
| Full official `RECORDS` catalog (84 IDs) | `invalid`; 84 header/annotation pairs inspected, 83 valid, only record `30` invalid, 0 complete waveforms. Provenance is verified for all 84. |
| Explicit `record_ids` list excluding `30` (83 IDs) | `valid`; 83 header/annotation pairs inspected, all valid, 0 complete waveforms. `record_count_in_catalog` remains 84 and provenance still covers all 84. |

Record 30's annotation sample 4,198,064 exceeds its declared final valid sample 2,826,239 by 1,371,825 samples. The `.hea`, `.atr`, official `RECORDS`, and acquisition-manifest SHA-256 values were unchanged by both read-only runs. The policy in `artifacts/research_readiness/stage8/RECORD_30_EXCLUSION_POLICY.json` explicitly documents this as candidate-cohort exclusion pending authoritative clarification; the 83-record call is only a temporary validation subset. Full-catalog validation remains invalid.

No LTAFDB model evaluation metrics were affected or recomputed: there is no current LTAFDB model/evaluation artifact, and this annotation/header-only validation does not establish signal-level or clinical validity. Historical derived label counts remain historical; they are not recalculated or promoted to performance metrics. The missing full waveforms remain a downstream blocker. No clinical validation or real cardiovascular-event prediction is supported by this subset result.

Regression coverage was added in `tests/test_ltafdb_validation.py` for explicit subset semantics, unchanged fixture catalog/record files, and retention of the original record 30 files in the manifested official catalog with the exclusion policy recorded.

## Phase 2 source/runtime delta (2026-10-23)

The nested source tree now adds `atria_twin/patient_twin_pipeline.py`, `atria_twin/patient_twin_dashboard.py`, and `atria_twin/evaluate_patient_twin.py`, changes `atria_twin/app.py` to connect the patient-linked replay/forecast, and adds `tests/test_patient_twin_pipeline.py` plus `tests/test_patient_twin_dashboard.py`. Related README, model card, architecture, and challenge/cleanup audit documentation was updated. This updated implementation remains source-only; it has not been copied into or promoted to the port-8501 runtime snapshot.

New artifacts are isolated under `artifacts/patient_twin_forecast_v1/` (retained and marked superseded) and `artifacts/patient_twin_forecast_v1_1/evaluation.json` (authoritative corrected report). The existing combined-model v1/v2 artifacts, static-model artifacts, source datasets, and original Record 30 files were checked against the pre-existing SHA-256 values in this report and all matched. The v1.1 report's recorded source SHA-256 values match the current `patient_twin_pipeline.py` and `patient_records.py`.

Verification at the Phase 2 point used `%TEMP%\\atria_twin_verify_20261023\\Scripts\\python.exe`. The selected suite passed **164 tests** with seven pandas deprecation warnings; this is historical and superseded by the Phase 3 update below.

## Phase 3 current runtime and preservation check — 2026-10-23

This section supersedes the earlier point-in-time statement that port 8502 had no listener. The old port-8501 service remains the temporary runtime copy; the current canonical nested source is now served separately on port 8502.

| Port | Listener / process | Served entry point | Final health check |
|---|---|---|---|
| 8501 | PID 4404 (parent PID 26248) | `%TEMP%\atria_twin_dashboard_6730286a\atria_twin\app.py` | `GET /_stcore/health` returned HTTP 200, `ok` |
| 8502 | PID 29228 (parent PID 27660); parent launched from `%TEMP%\atria_twin_verify_20261023\Scripts\python.exe` | Canonical nested source `atria_twin/app.py` | `GET /_stcore/health` returned HTTP 200, `ok` |

Source launch command, executed from the canonical nested source root:

```powershell
$python = Join-Path $env:TEMP 'atria_twin_verify_20261023\Scripts\python.exe'
& $python -m streamlit run atria_twin/app.py --server.headless true --server.address 127.0.0.1 --server.port 8502 --browser.gatherUsageStats false
```

The selected source tests were rerun in that isolated environment:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
& $python -m pytest -p no:cacheprovider --import-mode=importlib -q tests\test_atria_twin.py tests\test_data_readiness.py tests\test_ltafdb_validation.py tests\test_patient_twin_dashboard.py tests\test_patient_twin_pipeline.py tests\test_patient_workflow.py tests\test_runtime_dependencies.py tests\test_simulated_forecast.py tests\test_simulation_engine.py tests\test_stage4_safeguards.py tests\test_static_model.py tests\test_waveform_acquisition.py
```

Result: **169 passed, 35 warnings in 34.52 seconds** (two WFDB and 33 Streamlit/pandas deprecation warnings). Browser/AppTest coverage includes baseline versus scenario outputs, zero-default scenario controls, replay, and the main timeline's callback-based Reset to Baseline. This is UI/software evidence only.

Final SHA-256 checks recorded after the test run:

| Protected file | SHA-256 |
|---|---|
| `artifacts/patient_twin_forecast_v1_1/evaluation.json` | `18b85eda58f6370f5bb9c52f758c3b4b00f650933a6f9039c8081df8ff314a1` |
| `atria_twin/patient_twin_pipeline.py` | `64eca8cbde9728282902687dd849f55e29666ed281674e141f8912fff2cf21b2` |
| `atria_twin/patient_records.py` | `5e668d55e2bb66dbfae4447499ee859cce1a5fd217286a71c184b47af999f8c8` |
| `heart_disease_uci.csv` | `574f2fa2b43012fa25fca4fcdb36bd7c6bccdd0af4242f6c0e4c8633c5a072ae` |
| `work/ltafdb_annotations/30.hea` | `384635383f3b7c3914b6a2ce24dae8b65c5d1bc90a380293c36c691657a9145a` |
| `work/ltafdb_annotations/30.atr` | `3868fc9562d968365cd65f3c8603afba8806e8f5973c1ff75423c4dbbfc620da` |
| Source simulated-forecast model artifact | `7d49b26aa58adeabef03ddd708652cef6a36bf5e77083507521fafc0d688f634` |
| Source simulated-forecast evaluation | `a6031601d24e7b9704487b0e567a0984152c0604cc57e7111751df5644bfd69c` |
| Source static-model artifact | `d5ff2d5c2b8297a30dae61e8ec52d8fe41bf8ea0879d4576bb2a6646a17e8de8` |
| Source static-model evaluation | `7fead2b0e187ea9f6bc349badcd88db75b84d3656fa6fff8ac0874bb856db60f` |

These hashes document final protected-file state; they are not presented as a before/after diff for every project file. During the preceding Phase 3 check, no model training, artifact promotion, data acquisition, source environment repair, or security-setting change was performed. The later targeted port-8501 reset correction and controlled relaunch are recorded below. The source `.venv` SciPy issue remains unresolved; source serving and tests used the separate isolated environment.

## Port-8501 reset callback correction — 2026-10-23

The serving runtime `atria_twin/patient_dashboard.py` was stale relative to the canonical source. Its Reset to Baseline button used an `if st.button(...)` block, then called `reset_twin_controls()` and `st.rerun()`. That function assigned `twin_scenario_<patient_id>` after the selectbox for that key had already been instantiated, causing `StreamlitWidgetAlreadyInstantiatedError`. The canonical source already used the supported `st.button(..., on_click=reset_twin_controls, args=(patient_id,))` pattern.

The serving copy was corrected surgically at `%TEMP%\atria_twin_dashboard_6730286a\atria_twin\patient_dashboard.py`; no whole directory, model, or dataset was copied or overwritten. The runtime was relaunched at the same port using its existing interpreter and entry point. Port 8501 now listens on PID 9536 and returned HTTP 200 (`ok`); the separate source dashboard on port 8502 remained on PID 29228 and healthy. The final runtime module SHA-256 is `82025d8736647386fce548d2384601164454cb20133e779dcece91ecfd707952`; it is not expected to equal the canonical source module hash because the runtime copy has other pre-existing presentation differences.

The isolated verification environment ran `tests\test_patient_twin_dashboard.py`, `tests\test_patient_twin_pipeline.py`, and `tests\test_patient_workflow.py`: **41 passed, 42 Streamlit/pandas deprecation warnings in 28.93 seconds**. The reset regression verifies selection/override/timestep reset, repeated reset, patient isolation, and preservation of the telemetry replay state. Browser automation on the actual 8501 page clicked Reset to Baseline twice and confirmed the baseline selection remained visible with no widget exception. AppTest exercised reset after non-baseline scenario/offset changes. A browser-driven non-baseline reset was not verified because the scenario control did not reliably accept the automation selection; the UI reset itself was verified in-browser, and non-baseline behavior is covered by AppTest.

The user-facing reset affects only that patient's timeline scenario, HR/RMSSD offsets, and timestep. The independent telemetry replay cursor is preserved. The v1/v2 artifacts, static model artifacts, patient-twin evaluation, UCI dataset, and Record 30 files remain unchanged; the patient-twin evaluation SHA-256 remained `18b85eda58f6370f5bb9c52f758c3b4b00f650933a6f9039c8081df8ff314a1`.
