# Atria Twin project status

**Updated:** 2026-10-23  
**Scope:** Phase 3 source dashboard verification

## Current dashboard processes

| URL | Copy / interpreter | Status |
|---|---|---|
| `http://127.0.0.1:8501/` | Existing temporary runtime copy at `%TEMP%\atria_twin_dashboard_6730286a`; listener PID 9536 after the targeted reset-fix relaunch | Reset callback fix loaded; health endpoint returned HTTP 200 (`ok`) |
| `http://127.0.0.1:8502/` | Canonical nested source project using `%TEMP%\atria_twin_verify_20261023\Scripts\python.exe`; listener PID 29228 | Running; health endpoint returned HTTP 200 (`ok`) |

The canonical source root is `Thiranex--Heart-Disease-Prediction-Model-Using-ML-main (1)\Thiranex--Heart-Disease-Prediction-Model-Using-ML-main`. The Streamlit entry point is `atria_twin/app.py`. The source `.venv` remains unchanged and has a known incomplete SciPy installation; do not use it for this verified launch.

From the canonical nested source root, the verified launch command is:

```powershell
$python = Join-Path $env:TEMP 'atria_twin_verify_20261023\Scripts\python.exe'
& $python -m streamlit run atria_twin/app.py --server.headless true --server.address 127.0.0.1 --server.port 8502 --browser.gatherUsageStats false
```

## Verified application behavior

- The selected synthetic patient drives a stable patient ID, deterministic telemetry replay, chronological session-scoped twin state, a fixed 30-minute trend heuristic, and baseline-versus-scenario outputs.
- Replay and manual telemetry controls are session-scoped. Reset restores the seeded stream; the main timeline's Reset to Baseline uses a callback and was browser-checked without the prior widget-state exception.
- Neutral scenario controls default to zero change. Scenario outputs are illustrative, non-causal, and not medical recommendations.
- The forecast target is a synthetic threshold rule, not a fitted model, probability, clinical event, or clinically validated prediction.
- Existing UCI prevalent-label classification and older combined-input v1/v2 artifacts remain separate tasks.

## Tests and evidence

Executed in the isolated Python 3.12.10 environment:

```powershell
$python = Join-Path $env:TEMP 'atria_twin_verify_20261023\Scripts\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
& $python -m pytest -p no:cacheprovider --import-mode=importlib -q tests\test_atria_twin.py tests\test_data_readiness.py tests\test_ltafdb_validation.py tests\test_patient_twin_dashboard.py tests\test_patient_twin_pipeline.py tests\test_patient_workflow.py tests\test_runtime_dependencies.py tests\test_simulated_forecast.py tests\test_simulation_engine.py tests\test_stage4_safeguards.py tests\test_static_model.py tests\test_waveform_acquisition.py
```

**Result:** 169 passed, 35 warnings in 34.52 seconds. Warnings are pandas deprecations from two WFDB call sites and Streamlit chart rendering; there were no test failures.

Browser/AppTest checks covered the patient-linked replay controls, manual overrides, reset, neutral scenario defaults, baseline/scenario recomputation, and absence of Streamlit widget exceptions. HTTP checks to both dashboard health endpoints returned 200. These verify software operation only; they do not establish model quality or clinical validity.

## Preservation and remaining gaps

No model or dataset was replaced, deleted, retrained, or downloaded. The port-8501 service was briefly restarted with the same entry point after a callback-only correction in its temporary `patient_dashboard.py`; its port stayed 8501. Final SHA-256 checks are recorded in [COPY_COMPARISON.md](./COPY_COMPARISON.md), including the v1/v2 and static-model artifacts, the v1.1 synthetic evaluation, source inputs, and original LTAFDB Record 30 files. Windows security settings were not changed.

Remaining gaps: the synthetic patient-twin state is not durable across browser sessions; only three hand-authored fictional patient templates support the new synthetic evaluation; no clinical outcome labels, clinical validation, or real future-event prediction exist; public-repository publication is unverified; and the required 20–25 minute narrated video has not been recorded. Architecture/presentation exports have not been regenerated or visually reviewed after Phase 3.
