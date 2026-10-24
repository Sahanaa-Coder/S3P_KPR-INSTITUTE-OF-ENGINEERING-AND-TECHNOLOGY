# Safe Project Cleanup Plan

## Scope and safety

This is a read-only audit plan. No files were deleted, moved, renamed, reformatted, retrained, or overwritten. All data, model, evaluation, and provenance artifacts must remain in place until their consumers and compatibility are confirmed.

The inspected source tree contains 362 non-environment files. Content-hash checks found the exact duplicate pairs listed below. Static import reachability alone is not a safe basis for deleting code: the project also has documented command-line entry points, tests, dynamically selected modules, and a separate legacy application.

## Project identity and active copies

| Location | Audit finding | Cleanup implication |
|---|---|---|
| `Thiranex--Heart-Disease-Prediction-Model-Using-ML-main (1)/Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/` | Authoritative project root: contains `atria_twin/app.py`, `requirements.txt`, `tests/`, both datasets, source modules, and the current project artifacts. | Treat this as the source tree for any later approved cleanup. |
| `Thiranex--Heart-Disease-Prediction-Model-Using-ML-main (1)/` | Wrapper, not an application root: contains an old `.venv`, two distinct readiness reports, an empty `deliverables/`, and the authoritative project directory. | Do not mistake its environment or reports for the inner project's current runtime/artifacts. |
| `%TEMP%/atria_twin_project_6730286a/` | Short-path junction to the authoritative source root, not a second working copy. | Changes through this path affect the source tree. |
| `%TEMP%/atria_twin_dashboard_6730286a/` | Separate temporary runtime copy used by the running dashboard. Its navigation fix was mirrored there; it also has a simulated-forecast v2 artifact, unlike the source tree's v1 artifact. | Keep until the running server is stopped and its code/artifact differences are reconciled. Do not promote its model artifact as canonical without review. |

The source project's `.venv/pyvenv.cfg` identifies Python 3.12.10. The wrapper's separate `.venv/pyvenv.cfg` points to Python 3.14.6 under another user's profile and is not the project's active environment. The repository has no `.git` directory.

## Application, modules, and data flow

- **Atria Twin dashboard:** `streamlit run atria_twin/app.py` (or `.\.venv\Scripts\python.exe -m streamlit run atria_twin/app.py`). `atria_twin/app.py` composes the patient dashboard/workflow, data-readiness and evidence checks, static classifier, and forecast dashboard.
- **Separate legacy classifier:** root `app.py`, `predictor.py`, `data_loader.py`, `model_trainer.py`, `eda.py`, and `visualizer.py`. Root `app.py` directly reads the nine root PNGs and the root legacy model files. `main.py` is another documented legacy command-line entry point. Do not remove these files or their inputs as “unreachable from Atria Twin.”
- **Atria Twin source surface:** `atria_twin/` contains 39 files (36 Python files and 3 Markdown files). An AST reachability scan found 22 Python modules reachable from the Atria Twin entry point. The remaining Python files include documented research/acquisition/training commands, test targets, and modules whose use is not captured by a static import graph; none is established as safe to delete.
- **Stream A:** `atria_twin/patient_records.py` provides synthetic patient/EHR profiles and `fuse_patient_data`; this fusion is used to display patient/twin state.
- **Stream B and forecasting:** `atria_twin/simulated_forecast.py` creates wearable time-series features and combines their temporal aggregates with UCI clinical context features. Its target is simulator-rule-derived over a 30-minute horizon, not a measured clinical future outcome. This forecast path is separate from the display-level synthetic patient fusion.
- **Static classifier:** `atria_twin/static_model.py` trains/loads a classifier for the UCI prevalent-disease label (`num > 0`); it is not the simulated forecast model.
- **Data/readiness paths:** `atria_twin/audit_dataset.py` writes decision-window audit output; `atria_twin/data_readiness.py` and `atria_twin/evidence_status.py` inventory/check datasets, reports, and provenance. The dashboard reads those evidence outputs.

## Dataset, schema, provenance, and consumers

| Data | Observed schema/content | Provenance and consumers |
|---|---|---|
| `heart.csv` | 303 rows; 14 columns: `age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, target`. | Cleveland-style prevalent heart-disease data used by the legacy application/model flow and by readiness inventory. The root legacy loader expects `data/heart.csv` in some modes; the Atria Twin static model does not use this file. |
| `heart_disease_uci.csv` | 920 rows; 16 columns: `id, age, sex, dataset, cp, trestbps, chol, fbs, restecg, thalch, exang, oldpeak, slope, ca, thal, num`. | UCI Heart Disease source. `atria_twin/static_model.py` and `atria_twin/train_static_model.py` use it for the static label; `atria_twin/simulated_forecast.py` uses UCI context in simulated training. Evaluation JSON records the CSV SHA-256. |
| `work/ltafdb_annotations/` | 84 `.hea` headers, 84 `.atr` rhythm-annotation files, `RECORDS`, acquisition/waveform manifests and sidecar JSON; two interrupted `.dat.part` waveform downloads (`05` and `110`), with no complete `.dat` files in the inspected tree. | The project documentation identifies PhysioNet LTAFDB v1.0.0 and its ODC Attribution License. `atria_twin/download_annotations.py`, `download_waveforms.py`, `validate_ltafdb.py`, and the audit/readiness modules operate on this workflow. The partial files and manifests are resumable/provenance-bearing data, not disposable temporary files. |
| `artifacts/data_audit/decision_windows.csv` | 13,269 rows; columns `record, sample_rate_hz, decision_s, label, onset_s, lead_time_s`. | Generated by `atria_twin/audit_dataset.py`; consumed by Atria Twin audit/readiness/dashboard paths. Preserve as derived evidence. |
| Synthetic patient and wearable records | Defined in source rather than a standalone clinical dataset. Synthetic profile identities are not linked to UCI records or LTAFDB subjects. | `atria_twin/patient_records.py`, `atria_twin/simulated_forecast.py`, and simulation modules. Preserve the distinction in provenance and interpretation. |

## Model, evaluation, and evidence artifact map

| Artifact | Role / source or loader | Plan |
|---|---|---|
| `artifacts/static_model/uci_heart_logistic.joblib` and `uci_heart_evaluation.json` | Static UCI prevalent-label pipeline and evaluation; model implementation in `atria_twin/static_model.py`; dashboard integration in `atria_twin/app.py`. | Keep. |
| `artifacts/simulated_forecast/simulated_forecast_model.joblib` and `simulated_forecast_evaluation.json` | Forecast model and training/evaluation metadata; `atria_twin/simulated_forecast.py` trains/loads; `atria_twin/forecast_dashboard.py` loads and may retrain/save when the artifact is incompatible. The source-tree evaluation identifies model v1, while current code expects v2. | Keep and do not run training as cleanup. Confirm version compatibility before any replacement or promotion from the temporary runtime copy. |
| Root `best_model.joblib`, `scaler.joblib`, `feature_names.joblib` | Separate legacy classifier artifacts loaded by root `predictor.py`/`app.py`; Atria Twin explicitly treats them as non-AF artifacts. | Keep with the legacy app; do not conflate them with Atria Twin artifacts. |
| `artifacts/data_audit/` and `artifacts/research_readiness/` | 7 data-audit files and 76 readiness/stage files, including validation snapshots, manifests/reports, and derived evidence. | Keep. These are provenance and historical decision records, not disposable build output. |
| `backups/stage18_pre_upgrade/` | Six-file historical source/test snapshot. | Archive only after preserving the snapshot and checking any future traceability needs. |

## Proposed actions

### KEEP

- The complete authoritative source tree, `requirements.txt`, `LICENSE`, `README.md`, `EVENT_COMPLIANCE.md`, tests, tools, architecture/workflow documents, and model card.
- Both CSV datasets; the entire LTAFDB annotation/download directory (including `.part` files, sidecars, `RECORDS`, and manifests); every model/evaluation artifact; and all `artifacts/data_audit/` and `artifacts/research_readiness/` evidence.
- The source project's Python 3.12.10 `.venv` while it is the validated runtime. Do not clean or recreate it as part of file cleanup.
- The root legacy application, its three model files, and its nine `01_*.png` through `09_*.png` images. The PNGs are consumed by root `app.py`, so they are not unused merely because Atria Twin has a different entry point.
- Existing deliverables under `deliverables/` (PDF/PPTX, architecture image, silent AVI preview, and checklists). Their presence does not establish that the AVI is the required explanatory video; retain it pending separate deliverable review.
- The wrapper's two distinct readiness reports under `artifacts/research_readiness/phase1/` and `phase2/` until their ownership/history is reviewed.
- The active temporary dashboard copy until its server is stopped and source/artifact differences have been reconciled.

### ARCHIVE

- `backups/stage18_pre_upgrade/`: preserve as a clearly labeled historical snapshot; do not delete as a duplicate.
- Wrapper-level `.venv/`: candidate for quarantine/archive only after confirming no process or workflow uses it. It is tied to Python 3.14.6 under a different user profile and is distinct from the source project's Python 3.12.10 environment.
- The temporary dashboard runtime copy: after stopping its server, compare/retain its changed source and v2 model artifact before archiving the copy. It is not the canonical source tree.

### POSSIBLE DUPLICATE (verify)

- `artifacts/data_audit/input_validation.json` and `artifacts/research_readiness/stage14/full_catalog_validation.json` have identical SHA-256 content. They occupy different audit stages/paths and may represent intentionally retained evidence; verify provenance, consumers, and stage history before consolidating. Keep both meanwhile.
- `atria_twin/evidence_status.py` and `backups/stage18_pre_upgrade/atria_twin/evidence_status.py` have identical SHA-256 content. The matching backup file is part of a larger historical snapshot, so do not remove it independently.
- The wrapper folder and source folder are not duplicates as complete projects: the wrapper contains the source directory but its two readiness reports and old environment are separate items. Do not delete or merge the wrapper based only on its nested project name.

### SAFE TO REMOVE

Only after the active app/tests are stopped, a later cleanup is approved, and the paths are confirmed to be generated caches:

- `.pytest_cache/`.
- `__pycache__/` directories and `.pyc` files in the source tree (observed in the root, `atria_twin/`, its `simulation/` and `ui/` packages, `tests/`, and `tools/`).

No source module, dataset, model, evaluation, generated PNG, backup, or provenance/evidence file was found to be safe for removal in this audit. `desktop.ini` is Windows/OneDrive metadata and is intentionally not a removal candidate.

## Safe next-step order

1. Keep the authoritative source and evidence unchanged; separately reconcile the temporary runtime copy and its v2 forecast artifact.
2. If cleanup is later approved, remove only the identified caches first and rerun focused tests.
3. Decide whether the wrapper-level Python 3.14.6 environment and historical backup should be archived; preserve them until their ownership/use is clear.
4. Resolve the two hash-identical evidence pairs only with documented provenance/consumer confirmation. Do not consolidate model or data files by filename alone.

## Runtime/source reconciliation audit (2026-10-23)

See [COPY_COMPARISON.md](./COPY_COMPARISON.md) for the detailed SHA-256 comparison, evaluation metadata, and commands/results.

- Port `127.0.0.1:8501` is served by Streamlit using `%TEMP%\atria_twin_dashboard_6730286a\atria_twin\app.py`. The listener returned HTTP 200 at `/_stcore/health` (`ok`) and HTTP 200 at `/`. Port 8502 did not respond. The dashboard process and both temporary directories were left untouched.
- The runtime copy and source tree have identical contents/hashes for all 39 files under `atria_twin/` and both dataset CSVs. Of 87 shared artifact files, 83 are identical; the four differences are the static model/evaluation pair and simulated-forecast model/evaluation pair. No artifact file is missing or extra in either compared tree. The runtime copy is intentionally partial: it has no project `requirements.txt`, tests, docs, or tools; neither copy has a `.streamlit/` configuration directory.
- The source's `atria_twin/simulated_forecast.py` declares v2; the serving copy's forecast artifact/evaluation metadata also identify v2. The source tree's saved forecast artifact/evaluation identify v1, which is incompatible with that current source version. Source and runtime evaluation reports otherwise agree on the simulator target, 30-minute observation/horizon, five-minute sampling, dataset SHA-256, seeds, cohort/window counts, class counts, and recorded metrics.
- The v2 generation procedure is present and deterministic in `atria_twin/simulated_forecast.py`: 300 fictional profiles split 225/75, 4,500 training windows and 1,500 holdout windows, UCI-context SHA-256 `574f2fa2b43012fa25fca4fcdb36bd7c6bccdd0af4242f6c0e4c8633c5a072ae`, training seed `240823`, and train/test seed `42`. Its 37 raw model columns comprise 13 UCI clinical fields plus 24 temporal aggregates (mean, slope/minute, latest) across eight synthetic wearable measurements. The forecast label is generated from future synthetic measurements; the evaluation explicitly records `clinical_validation: false` and `real_event_prediction: false`.
- This establishes that the v2 result is reproducibly specified by available source and data, but **does not establish a successful fresh reproduction or validate the serialized model/predictions on this laptop**. `joblib.load`/training could not be completed: the source venv's SciPy import fails because `scipy.optimize._trustregion_constr.minimize_trustregion_constr` is missing, and pytest is not installed. The saved JSON metrics remain reported metadata, not newly recomputed results.
- Therefore, the runtime copy is the **most internally version-consistent candidate** (v2 code and v2 forecast artifacts); neither copy can be designated the currently verified/tested canonical release from this audit. Keep the source tree authoritative and preserve the running dashboard; do not copy or replace artifacts until the procedure below is approved and all checks pass.

### Proposed reconciliation procedure — not executed

1. **Freeze and identify:** leave the live dashboard running and untouched. Record the full source/runtime paths, process IDs, listening port, and baseline SHA-256 values for every file in `atria_twin/`, `artifacts/`, both CSVs, and `requirements.txt`. Do not use the short-path junction as though it were a second copy.
2. **Create a recoverable backup before any approved change:** after explicit approval, copy (do not move) the complete destination artifact directory and any source file proposed for replacement to a new, uniquely named backup directory outside both trees. Preserve directory structure and copy metadata where available. Hash every backup file and compare it to its pre-copy source; abort if any hash differs. Keep the original backup untouched until acceptance.
3. **Resolve validation blockers without modifying this project:** first diagnose/restore the missing SciPy package file and provide pytest in an explicitly approved test environment; do not install packages or change security controls as part of this audit. Re-run imports, the focused/full tests, and check that no project artifact hashes changed.
4. **Reproduce into an isolated staging directory:** run the v2 trainer from the source tree with the recorded dataset and seeds, using a new staging artifact directory outside the repository. Confirm the dataset hash, model version, required input columns, cohort/split metadata, evaluation JSON, and prediction outputs; do not train directly into either source or serving artifact directory.
5. **Compare before promotion:** require a successful v2 loader, independent sample inference through the real `predict_simulated_anomaly` path, and agreement between the staged run's metadata/metrics and the v2 report. Treat serialized model hash equality as desirable but not required if serialization is nondeterministic; compare fitted behavior/predictions and complete provenance instead. Verify the simulated-only interpretation remains explicit.
6. **Stage a candidate without disturbing the live process:** only after all checks pass and with approval, prepare a separate candidate copy and smoke-test it on a non-conflicting port. Confirm the existing 8501 process still serves its original path and retain the baseline hashes.
7. **Promotion and rollback:** only with explicit approval, stop/restart the service against the selected candidate and verify HTTP health plus real inference. If startup, tests, artifact validation, or inference fail, restore the saved destination files from the hash-verified backup (copy back, never delete the backup), restart the prior known-serving path, and confirm port 8501 health. Preserve both copies until the rollback window closes.

No copy, backup, package repair in the source environment, artifact replacement, cleanup, or server restart was performed during this audit. A separate temporary verification environment successfully loaded and reproduced the runtime v2 forecast artifact; see `COPY_COMPARISON.md`. The project test suite passed there. No clinical validation or real cardiovascular-event prediction was established.

## LTAFDB retention and evidence audit (2026-10-23)

The following inventory was checked read-only. The full local LTAFDB validation parsed all 84 records and verified the local acquisition manifest/file hashes, but returned **invalid**: 83 valid records and record `30` invalid for one annotation outside the header-declared signal length. There are **zero complete `.dat` waveform files**. The incomplete `.dat.part` files are resumable data with per-chunk sidecars. The validator's checks establish local integrity and parse/bounds behavior, not clinical quality or independent adjudication.

### File classification

| Classification | Exact paths/patterns | Evidence and reason |
|---|---|---|
| **KEEP** | `work/ltafdb_annotations/RECORDS`; `acquisition_manifest.json`; `waveform_manifest.json` | Catalog/provenance and incomplete acquisition state. Manifest records source, version, license, citation/acknowledgment, local sizes and hashes. The hashes are local-manifest checks, not PhysioNet-signed verification. |
| **KEEP** | For each of the 84 IDs listed in `work/ltafdb_annotations/RECORDS`, `work/ltafdb_annotations/<ID>.hea` and `work/ltafdb_annotations/<ID>.atr` (84 headers + 84 annotation files) | Raw source headers and PhysioNet-provided reference rhythm annotations. All corresponding files are in the acquisition manifest; 83 pairs pass strict parsing, and record 30 remains preserved but invalid under the strict bounds check. SHA-256 scan found no byte-identical duplicate among these 168 raw files. |
| **KEEP** | `work/ltafdb_annotations/05.dat.part`, `05.dat.part.json`, `110.dat.part`, `110.dat.part.json` | Partial waveform downloads and resumable chunk metadata. Neither is a complete waveform; do not remove as generic temp files or rename/merge them. The incomplete waveform manifest remains `in_progress`. |
| **KEEP** | `artifacts/data_audit/record_30_diagnostic.json`, `record_30_semantics_review.md`, `record_30_followup_status.md`, `physionet_record_30_clarification_request.md` | Preserve the specific unresolved source-data discrepancy, interpretation, and communication history. No authoritative maintainer resolution is recorded. |
| **ARCHIVE (retain in place; historical, not current model evidence)** | `artifacts/data_audit/audit_summary.json` and `artifacts/data_audit/decision_windows.csv` | Prior deterministic annotation-derived audit output. The summary records 84 audited records, 7,316 annotated AF intervals, 76 unique eligible onset times, 312 positive windows, and 12,957 negative windows. It predates strict record-30 rejection and must not be presented as a current validated evaluation or as 76 independent clinical events. The CSV contains 13,269 annotation-derived decision windows, not an independently adjudicated outcome table. Keep the files and their current paths until a separately approved archival plan. |
| **POSSIBLE DUPLICATE (keep both pending provenance review)** | `artifacts/data_audit/input_validation.json` and `artifacts/research_readiness/stage14/full_catalog_validation.json` | Exact SHA-256 duplicate: `a6397a21af824d0e6af805f1a3e8f24d37e7ae825fab8bd11eca931b0fbd7108`. They are used as stage-specific evidence paths; identical bytes do not prove either path is redundant. No other exact duplicate group was found in the 258 hashed files spanning local LTAFDB data, data-audit evidence, and research-readiness artifacts. |
| **KEEP** | Every file under `artifacts/research_readiness/stage*/` (76 files across existing stages) | Historical validation, integrity, causal-feature, cohort, licensing, acquisition, and test/readiness evidence. Stage 8 `eligible_cohort.json` exists and is referenced by the waveform manifest; it is an acquisition-selection record, not evidence of complete waveforms, a patient-linked cohort, or model evaluation. Stage 13/14 report variants have different hashes except the duplicate pair above and must not be treated as interchangeable. |
| **KEEP** | `atria_twin/download_annotations.py`, `download_waveforms.py`, `validate_ltafdb.py`, `diagnose_record.py`, `select_cohort.py`, `cohort.py`, `labels.py`, `audit_dataset.py`, `build_features.py`, `features.py`, `modeling.py`, `data_gate.py`, `data_readiness.py`, `evidence_status.py`, and `app.py` | Current acquisition, parsing, strict validation, annotation-label/window construction, gated feature/evaluation, readiness, and dashboard integration code. These are referenced by the current code/tests/docs; no unused/deletion candidate was established. |
| **KEEP** | `tests/test_ltafdb_validation.py`, `test_waveform_acquisition.py`, `test_stage4_safeguards.py`, `test_data_readiness.py`, and LTAFDB-related cases in `test_atria_twin.py` | Automated tests for validation, manifest provenance, download/resume behavior, label/window safeguards, readiness, and dashboard status. They primarily use temporary fixtures and do not independently validate clinical labels. |
| **KEEP** | `atria_twin/DATA_FEASIBILITY.md`, `atria_twin/README.md`, `atria_twin/MODEL_CARD.md`, root `README.md`, `docs/RESEARCH_STATUS_AND_LIMITATIONS.md`, `docs/PATIENT_TWIN_WORKFLOW.md`, `docs/SUMMIT_DEMO_SCRIPT.md`, `docs/SUMMIT_PRESENTATION_OUTLINE.md`, and LTAFDB-related reports under `artifacts/research_readiness/stage*/` | Document source provenance/attribution, unresolved record-30 failure, missing waveforms, unverified XQRS causality, closed feature/model gates, and limits on claims. Preserve to avoid losing the non-clinical interpretation and audit trail. |
| **CANDIDATE FOR REMOVAL** | None | No LTAFDB raw, partial, derived, source, test, provenance, or evaluation-evidence file is proven redundant and dependency-free. Do not remove anything in this phase. |

### Annotation and evaluation validity

The `.atr` files are source-provided reference rhythm annotations. The project parser deterministically derives AF intervals, then positive/negative decision-window labels using the stated minimum episode duration, clean lookback, minimum lead time, and forecast horizon. This makes the decision-window labels **derived from reference annotations**, not labels independently adjudicated or clinically revalidated by this repository. Local SHA-256 and WFDB parse/bounds checks do not certify source authenticity or clinical ground truth. The record-30 failure means the strict whole-catalog workflow is not currently valid; retain the source files and keep downstream gates closed.

The saved historical audit can be interpreted as a reproducible annotation-count/window derivation in principle, but it cannot currently be promoted as the result of a successful strict end-to-end pipeline: current validation rejects record 30, no complete ECG waveforms are present, no current feature table or AF-onset model/prediction/evaluation artifact is present, and the causal detector gate remains unverified. The 76 eligible onsets are unique onset times under the code's counting rule, not evidence of 76 independent patients/events or clinical model performance.

The passing tests verify software behavior and synthetic fixtures only. They do not establish independent annotation accuracy, waveform quality, clinical utility, or a valid AF event forecasting result. The v2 model reproduced in `COPY_COMPARISON.md` is separately based on generated wearable anomalies and UCI context; it does not consume LTAFDB records and must not be described as an LTAFDB/AF model.

### Safe backup and rollback procedure before any future approved data action

No LTAFDB action is approved or performed here. If a future, explicitly approved operation would alter these paths:

1. Leave the port-8501 dashboard and its temporary runtime tree untouched; separately record process/path and baseline hashes.
2. Make a **copy**, never a move, of the entire affected `work/ltafdb_annotations/` or artifact directory into a new, uniquely named backup outside the source tree. Preserve filenames, relative paths, file sizes, and metadata when supported.
3. Recompute SHA-256 for every source and backup file; abort if a file is missing or any copied hash differs. Keep the original and backup unchanged until the change is reviewed and accepted.
4. Perform validation or any generated output in a separate staging directory, never over raw `.hea`, `.atr`, `.dat.part`, manifests, or existing evidence. Capture the command, environment, source-manifest hash, output hashes, and validation status.
5. If any check fails or output differs unexpectedly, restore by copying from the verified backup (do not delete the backup), re-hash restored files, rerun the read-only strict validator, and confirm the 8501 health endpoint remains unchanged.

The verification and LTAFDB status in this section supersede earlier provisional environment/model statements in this plan. The serving copy remains v2-consistent; the source environment remains unmodified and SciPy-incomplete; and the LTAFDB strict validation remains blocked on record 30.

## Record 30 validation-subset comparison (2026-10-24)

Read-only validation ran in `%TEMP%\atria_twin_verify_20261023` against `work/ltafdb_annotations/`, with `require_waveforms=False` and no report output path. The two calls were `validate_ltafdb(data_dir, require_waveforms=False)` and `validate_ltafdb(data_dir, require_waveforms=False, record_ids=[record_id for record_id in RECORDS if record_id != "30"])`.

| Scope | Result | Evidence |
|---|---|---|
| All 84 official records | **INVALID**: 84 header/annotation pairs inspected, 83 valid, 1 invalid (`30`); 0 complete waveforms. | Only error: annotation 31,190 at sample 4,198,064 exceeds record 30's declared 2,826,240 samples (last valid index 2,826,239). Acquisition provenance verified for all 84 records. |
| Explicit temporary 83-record subset | **VALID** for annotation/header checks: 83 pairs inspected, all 83 valid; 0 complete waveforms. | `record_ids` omits `30`; catalog count remains 84 and acquisition provenance still verifies all 84 manifest records. The subset does not rewrite `RECORDS` or change the full-catalog result. |

The bounds mismatch is in the annotation timestamp relative to the header-declared recording bounds; it is not caused by absent `.dat` waveforms. Record 30 remains present in `RECORDS`, the acquisition manifest, and on-disk `.hea`/`.atr` files. Before/after SHA-256 was unchanged for `30.hea` (`384635383f3b7c3914b6a2ce24dae8b65c5d1bc90a380293c36c691657a9145a`), `30.atr` (`3868fc9562d968365cd65f3c8603afba8806e8f5973c1ff75423c4dbbfc620da`), `RECORDS` (`55008932b1e44d4faccec2b75db73ee90707742d9e3a4d238c789c838fd8d7a2`), and `acquisition_manifest.json` (`c3b87c10f192ac4eaa60e58497e1a31f8014a320a9b9f77b0958fdb7afe186bf`).

This is an explicitly filtered validation comparison using the existing `record_ids` API, not a correction or replacement of the official catalog and not a relaxation of strict full-catalog validation. The existing Stage 8 policy continues to restrict its exclusion decision to candidate-cohort selection pending authoritative clarification. A regression test covers the subset behavior and separately verifies that original record 30 remains manifested and explicitly named by that policy.

No model evaluation metrics were recalculated or changed: the repository has no current LTAFDB-derived model/evaluation, and absent complete waveforms remain a downstream blocker. Historical annotation-derived counts remain historical and are not made valid performance metrics by this subset pass. No clinical validation or real-event prediction is established.

## Phase 2 patient-linked twin implementation (2026-10-23)

The nested source tree now contains a separately versioned patient-linked synthetic replay/forecast path in `atria_twin/patient_twin_pipeline.py` and `atria_twin/patient_twin_dashboard.py`, integrated through `atria_twin/app.py`. Its write-once report is `artifacts/patient_twin_forecast_v1_1/evaluation.json`; the earlier report in `artifacts/patient_twin_forecast_v1/evaluation.json` is retained and marked superseded because its method wording incorrectly implied cross-validation. Neither report is clinical evidence. The prior `artifacts/simulated_forecast/` v1/v2 model/evaluation artifacts remain separate and must not be treated as outputs of the patient-linked rule.

The Digital Twin session supports deterministic start/pause/resume/step/reset/speed, chronological state, manual session-only HR/RMSSD/SBP overrides, forecast refresh, and synthetic scenarios. Reset restores the seeded readings and does not alter patient records or datasets. Replay state is not durable across browser sessions or process restarts. New tests are in `tests/test_patient_twin_pipeline.py` and `tests/test_patient_twin_dashboard.py`; the isolated selected suite passed 164 tests with seven pandas deprecation warnings (two WFDB, five Streamlit chart).

The port-8501 server and `%TEMP%\\atria_twin_dashboard_6730286a` runtime snapshot were not modified or restarted. Source-tree changes are not present in that runtime snapshot unless separately reconciled and promoted after explicit review. No cleanup action is authorized by this implementation note.

## Phase 3 runtime and documentation status — 2026-10-23

The earlier port status above is historical and is superseded for current operation by the following separate-server arrangement:

| Port | Role | Final check |
|---|---|---|
| `127.0.0.1:8501` | Existing temporary runtime copy, PID 4404; no changes made | Streamlit health endpoint HTTP 200 (`ok`) |
| `127.0.0.1:8502` | Canonical nested source, isolated Python 3.12.10 environment, PID 29228 | Streamlit health endpoint HTTP 200 (`ok`) |

No cleanup action was performed. Phase 3 changes were limited to the patient twin dashboard/reset behavior, its tests, and consistency updates to README, audit/comparison/cleanup records, architecture text/diagram, model card, demo script/checklist, plus a new root `STATUS.md`. The source datasets, LTAFDB record 30, prior static and simulated-forecast artifacts, and versioned patient-twin evaluation remain protected. See [COPY_COMPARISON.md](./COPY_COMPARISON.md) for final SHA-256 values.

The selected source test command completed with **169 passed, 35 pandas deprecation warnings in 34.52 seconds** using `%TEMP%\atria_twin_verify_20261023\Scripts\python.exe`. The original source `.venv` and its missing SciPy module were not repaired. Streamlit AppTest and browser QA verified the user-facing reset callback, replay state, zero-default scenario values, and baseline-versus-scenario recomputation. These are software checks, not model/clinical validation.

The source entry point remains `atria_twin/app.py`; the verified current-source launch command (from the nested source root) is:

```powershell
$python = Join-Path $env:TEMP 'atria_twin_verify_20261023\Scripts\python.exe'
& $python -m streamlit run atria_twin/app.py --server.headless true --server.address 127.0.0.1 --server.port 8502 --browser.gatherUsageStats false
```

Remaining delivery gaps are not cleanup candidates: twin state is browser-session scoped, generated data/outcomes are synthetic, no clinical validation or real event prediction is established, public GitHub publication is unverified, and the required narrated video is still pending. Existing architecture/presentation exports have not been regenerated or visually re-reviewed. No artifact promotion, source-environment repair, dataset acquisition, security setting change, or action on the 8501 service occurred.
