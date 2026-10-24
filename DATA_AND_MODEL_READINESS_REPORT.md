# Atria Twin Phase 1: Data and Prediction Readiness

**Review date:** 2026-10-22  
**Scope:** Read-only inspection of the existing application, local research inputs, audit artifacts, tests, and official PhysioNet dataset descriptions. No application changes, data acquisition, or model training were performed.

## Decision

**A defensible predictive model is not feasible with the data currently accessible in this checkout.** The 84 LTAFDB headers and rhythm-annotation files are present, but there are no complete ECG waveforms, no feature table, and no trained or evaluated Atria Twin AF model. Feature extraction is explicitly blocked because XQRS decision-time causality is unverified. The existing patient fusion and simulation paths contain fictional demo data and do not feed an AF model.

There is a promising public alternative for a **separate, narrowly defined PAF-onset challenge replication**: the PhysioNet PAF Prediction Challenge Database (AFPDB). Its curated precursor/distant examples and published subject-level learning/test organization are more prediction-specific than a database that merely contains AF. It does not establish the current Atria Twin 5-to-30-minute target, and it is not locally acquired or evaluated. No model or performance claim follows from its availability.

## 1. Current Architecture and Relevant Interfaces

The checkout contains two distinct pipelines. The legacy root application uses the UCI-style `heart.csv` status-classification dataset and saved classifier artifacts; it is not an AF-onset model. Atria Twin is a separate Streamlit application with five workspaces. Its patient directory, fusion, and simulation are synthetic-only and intentionally isolated from the ECG research workflow.

| Concern | Existing implementation and interface |
|---|---|
| Five workspaces and artifact gates | [`atria_twin/app.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/app.py) defines Digital Twin, Patient Overview, Clinical Assessment, Research & Validation, and Synthetic Clinic. It loads only Atria Twin artifacts and withholds predictions without current hash-verified outputs. |
| Local dataset inventory | [`atria_twin/data_readiness.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/data_readiness.py) scans files and tabular structure; it does not assess waveform quality or infer patient linkage. |
| LTAFDB acquisition and validation | [`atria_twin/download_annotations.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/download_annotations.py), [`atria_twin/download_waveforms.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/download_waveforms.py), [`atria_twin/validate_ltafdb.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/validate_ltafdb.py), and [`atria_twin/data_gate.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/data_gate.py) provide provenance-aware, fail-closed acquisition/validation gates. |
| Rhythm labels | [`atria_twin/labels.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/labels.py) parses WFDB rhythm transitions and builds five-minute decision windows with a 30-minute AF-free lookback, a 5-minute minimum lead, a 30-minute horizon, and a 30-second minimum AF episode duration. |
| ECG feature extraction | [`atria_twin/features.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/features.py) defines RR-derived HR/HRV features and past-only personal baselines. Extraction calls XQRS on the whole recording and refuses to proceed while `XQRS_TEMPORAL_CAUSALITY` is `unverified`. |
| Feature artifact generation | [`atria_twin/build_features.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/build_features.py) requires a validation report and records source hashes and cohort provenance. |
| Model/evaluation | [`atria_twin/modeling.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/modeling.py) defines fixed-schema logistic baselines, record-grouped `GroupKFold`, window and event metrics, and recording-cluster bootstrap intervals. [`atria_twin/train_model.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/train_model.py) is its CLI entry point. Evaluation also rejects feature artifacts without verified causality and current source hashes. |
| Synthetic patient records and fusion | [`atria_twin/patient_records.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/patient_records.py) defines three fictional patients and `fuse_patient_data`; [`atria_twin/patient_workflow.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/patient_workflow.py) passes the synthetic baseline only to the demo twin. This fusion does not enter the ECG feature table or model. |
| Simulation and risk status | [`atria_twin/simulation/engine.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/simulation/engine.py) produces deterministic hypothetical observations. [`atria_twin/patient_dashboard.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/patient_dashboard.py) displays an unweighted factor inventory; risk remains unavailable. |
| Legacy classifier | [`data_loader.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/data_loader.py), [`model_trainer.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/model_trainer.py), root `heart.csv`, and root `best_model.joblib`/`scaler.joblib`/`feature_names.joblib` concern existing heart-disease status, not future AF onset. `data_loader.py` can synthesize a fallback dataset if its local CSV and optional UCI fetch are unavailable; that fallback must not be mistaken for patient evidence. |

The architecture and current separation are also recorded in [`docs/ARCHITECTURE.md`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/docs/ARCHITECTURE.md), [`docs/RESEARCH_STATUS_AND_LIMITATIONS.md`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/docs/RESEARCH_STATUS_AND_LIMITATIONS.md), [`atria_twin/README.md`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/README.md), and [`atria_twin/MODEL_CARD.md`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/MODEL_CARD.md).

## 2. Dataset Availability and Integrity

### Local inputs

| Data | Present state | Readiness meaning |
|---|---|---|
| PhysioNet LTAFDB v1.0.0 | Local `work/ltafdb_annotations/` contains the catalog, 84 `.hea` files, 84 `.atr` files, and an acquisition manifest. Headers declare two ECG leads at 128 Hz, 12-bit, generally 20–25 hours. | The saved strict validation reports 83 valid and 1 invalid record. Record `30` has a trailing annotation at sample 4,198,064, beyond its header-declared 2,826,240 samples. A source comparison found the local `.hea` and `.atr` byte-identical to official files; the meaning of the trailing Aux marker remains unresolved. The validator’s bounds rule is not relaxed here. |
| LTAFDB waveforms | No complete `.dat` exists locally. `05.dat.part` and `110.dat.part` and resume journals are present; their transfers are incomplete. The waveform manifest is `in_progress`, with no finalized file hashes or completed candidate records. | No local waveform can be used for feature generation or signal-quality review. The previously approved acquisition scope was `05`, `110`, `118`, `20`, and `37`; its interrupted status is not evidence that those five waveforms are usable. |
| Saved annotation audit | [`artifacts/data_audit/audit_summary.json`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/artifacts/data_audit/audit_summary.json) reports 7,316 AF intervals, 76 candidate onsets in 53 recordings, 312 positive and 12,957 negative windows. | These are provisional annotation-derived counts: the audit includes Record `30` and predates enforcement of the strict full-catalog gate. They are not waveform validation, a finalized cohort, feature coverage, or model performance. Do not use them as confirmed training counts. |
| Legacy `heart.csv` | 303 rows, 14 columns, an existing heart-disease status target; no longitudinal timestamp, stable person/record identifier, waveform, or rhythm annotation. | Not suitable for AF-onset prediction, patient-specific temporal fusion, or grouped AF evaluation. |
| Patient/workspace data | Three hand-authored `DEMO-AT-*` patient profiles and simulated wearable-style observations in source code. | Fictional application fixtures only; no real EHR, wearable, or patient linkage. |
| Atria Twin outputs | The workspace-level `artifacts/` contains no local Atria Twin feature or model output directories; the nested project’s saved audit/readiness evidence is described above. | No current feature table, AF model, out-of-fold prediction artifact, or valid AF evaluation is available. Legacy classifier artifacts do not fill this gap. |

The read-only `python -m atria_twin.data_readiness` inventory was run from the nested project root. The local filesystem and waveform manifest independently confirm the incomplete waveform state. Annotation samples are interpreted against each header’s declared sample rate and duration; the saved validation reports consistent 128 Hz metadata and readable annotations for the 84 records, while rejecting Record `30` for the boundary mismatch. It would be unsafe to treat the 84-record annotation audit as wholly validated until the source discrepancy is authoritatively resolved or the existing policy is applied without weakening validation.

### Identifiers, licenses, and access

LTAFDB record IDs support **recording-grouped** evaluation. No verified record-to-person map is present, so a record split must not be described as a patient-independent split. The version-specific PhysioNet page associates LTAFDB v1.0.0 with the Open Data Commons Attribution License v1.0 (ODC-By). Preserve the requested dataset/PhysioNet citations and the `atr` annotation acknowledgment to MEDICALgorithmics Ltd, coordinated by Michal Tadeusiak. The license designation does not by itself settle privacy, ethics, or rights in individual contents. See the existing [`Stage 12 license resolution`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/artifacts/research_readiness/stage12/STAGE12_LICENCE_RESOLUTION.md).

## 3. Alternative Public Dataset Assessment

### PAF Prediction Challenge Database (AFPDB)

The official PhysioNet [AFPDB v1.0.0 page](https://physionet.org/content/afpdb/1.0.0/) describes a dataset made specifically for the Computers in Cardiology 2001 challenge on predicting paroxysmal AF. It is open access under ODC-By v1.0; the page says anyone may access files subject to the license. The listed uncompressed collection is about 191.4 MB. No AFPDB files are present in this checkout.

The learning set has 50 record sets from 48 subjects. Each set contains two consecutive 30-minute records and two 5-minute continuation excerpts. In PAF sets, the even-numbered 30-minute record immediately precedes a PAF episode, verifiable in its continuation; the odd-numbered record is described as distant from PAF, with no PAF in the surrounding 45-minute periods. The non-PAF records are from subjects without documented AF. The separate test set has 50 record sets from 50 different subjects, with paired consecutive records and no continuations. Records are two-channel ECG sampled at 128 Hz. Challenge-provided `.qrs` files are machine-generated and explicitly unaudited; they should not be treated as reference QRS truth.

This is the strongest public alternative found for a **separate challenge-replication task**, because the precursor and distant-record conventions and the subject-grouped split are explicit. It does **not** establish the Atria Twin target of a newly annotated AFIB interval 5–30 minutes after each rolling decision point. Before adopting it, verify the exact AF onset/rhythm in continuation annotations, define the prediction timestamp and horizon from those records, preserve subject-set grouping, and do not tune on the public test set. Its small, selected PAF cohort and curated case/control construction limit generalization; it contains no linked EHR or wearable stream.

### MIT-BIH Atrial Fibrillation Database (AFDB)

The official [AFDB v1.0.0 page](https://physionet.org/content/afdb/1.0.0/) describes 25 long-term AF recordings; 23 have two-channel waveform files. They are 10 hours each, sampled at 250 Hz, with manual rhythm annotations including AF, flutter, junctional, and other rhythms. The page lists open access and ODC-By v1.0. Unlike AFPDB, AFDB is a collection of AF recordings, not an explicit precursor-versus-distant prediction challenge. Rhythm transitions alone do not define a validated onset forecasting cohort or patient-independent split. It is therefore not a drop-in solution to the prediction task without a separately specified and justified protocol.

## 4. Candidate Prediction Task and Feasibility

### Existing LTAFDB research target

The implemented label function defines one candidate task: at decision time `t`, predict whether an annotated AFIB interval of at least 30 seconds begins in `[t + 5 minutes, t + 30 minutes]`. Candidate decisions occur every five minutes, with a complete 30-minute known-rhythm, AF-free lookback. A point is excluded if AF is active or occurred in that lookback, the next eligible onset is less than five minutes away, rhythm history is not yet known, or the complete future horizon is unavailable. A negative requires complete annotated follow-up through the horizon and no qualifying onset; incomplete annotation or recording boundaries must never become a negative by default. **Code-review caveat:** `build_decision_windows` filters future episodes to those lasting at least 30 seconds before finding the next onset. A short AFIB episode in the forecast horizon can therefore be ignored and the window labeled negative. Phase 2 must either exclude any horizon containing AFIB of any duration or predefine and justify why sub-30-second AFIB is a valid negative for this outcome; add a regression test before creating labels.

This label can be constructed from future annotations **as an outcome only**, while keeping all predictors restricted to data available at or before `t`. It is an exploratory short-horizon forecasting target in a cohort already selected for paroxysmal/sustained AF, not general-population screening. Repeated five-minute rows and multiple positive rows near one onset are correlated; windows are not independent samples. The 30-second duration threshold is a declared engineering convention, not a clinical diagnosis rule.

### Feasibility conclusion

The target is definable and the label code includes conservative exclusions, but current local data cannot support a defensible model: waveforms are absent, one source annotation/header pair fails strict validation, the current detector’s temporal causality is unresolved, and no evaluation artifact exists. Even after obtaining waveforms, the approved five-record sample is an acquisition pilot, not a sufficient independent evaluation cohort. LTAFDB does not supply patient linkage or multimodal EHR/wearable inputs. Patient-specific synthetic fusion cannot be used to claim a gain in AF prediction.

AFPDB may support a different, narrow PAF-challenge replication after its labels and continuations are explicitly audited. Do not merge its task, subjects, or metrics with LTAFDB’s rolling 5–30-minute target. A challenge replication would not establish clinical usefulness or enable the Atria Twin patient risk panel.

## 5. Reproducible Protocol Proposal

This proposal applies to the existing LTAFDB target only after the explicit blockers below are cleared. It is not authorization to acquire data, extract features, train, or display predictions.

1. **Prediction time and input window:** define `t` on the ECG sample clock. Use only ECG samples and independently timestamped covariates observed no later than `t`; the current ECG window is `[t - 30 minutes, t]`. A detector may only emit peaks/features whose evidence and confirmation latency are available by `t`. Do not use annotations, future samples, whole-record transforms, or future-derived initialization as predictors.
2. **Forecast horizon and label:** use the existing 5–30-minute interval after `t`. Positive means a rhythm-annotated AFIB interval begins in that horizon and lasts at least 30 seconds. Audit marker semantics and sample/time conversion at the source rate before freezing labels.
3. **Negative eligibility:** require valid, complete signal and known rhythm over the full lookback and through the full 30-minute horizon. Require no AF in the lookback and, conservatively, no AFIB annotation of any duration in the forecast horizon; otherwise exclude the window unless a sub-30-second episode is explicitly justified as a negative for the prespecified target. Exclude active AF, onset inside the minimum five-minute lead, unknown rhythm, invalid/incomplete records, and signal windows failing predeclared quality rules; do not coerce excluded or unobserved intervals to zero.
4. **Signal preprocessing/features:** predeclare lead selection, calibration, artifact/quality checks, filter passband, detector, initialization, warm-up, and peak timestamp/confirmation rules. Use causal filters with persistent state; never use forward-backward filtering or whole-record normalization for a decision-time feature. Begin with the existing HR/SDNN/RMSSD/pNN50 summaries. Fit imputation, scaling, and any learned transformations within training folds only. Past-only individual baselines are permissible only when computed from earlier available windows. Annotation-history features remain an offline retrospective comparator, not an online predictor.
5. **Cohort and splits:** freeze an outcome-independent cohort manifest before feature or outcome inspection. Group all windows from a person into one partition if a verified person key is obtained. If only record IDs remain available, group by record, report that unit honestly, and make no patient-independence claim. Keep a final grouped test set untouched; use grouped training/validation partitions for model selection and ensure both classes are represented. Five records cannot support a credible final evaluation. Do not use AFPDB test records to tune an LTAFDB model or combine datasets without a prespecified external-validation design.
6. **Comparators and metrics:** compare training-prevalence and simple HRV baselines with the prespecified ECG model on identical folds. Report window-level precision, recall, average precision/PR-AUC, ROC-AUC only when both classes occur, confusion matrix at a prespecified threshold, and Brier score with no calibration claim. Report event sensitivity, missed events, false alerts per recording-hour/day, event-alert precision, duplicate alerts/cooldown policy, median lead time, and usable-feature/event coverage. No threshold tuning on final test data.
7. **Uncertainty and calibration:** calculate 95% intervals by resampling whole independent groups, not overlapping windows. Use patient-cluster intervals only if person IDs are verified; otherwise name them recording-cluster intervals. Report too-few-group/class conditions as not estimable. Assess calibration only on adequate independent validation data; Brier score alone is not evidence of calibration. No metrics or confidence intervals have been calculated for this phase.

## 6. Tests Required to Establish Temporal Causality

Existing safeguards include bounded RR-feature windows, future-annotation isolation tests, past-only baseline tests, and a deterministic toy-signal XQRS prefix/perturbation fixture in [`tests/test_stage4_safeguards.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/tests/test_stage4_safeguards.py). The extraction gate correctly remains closed. Toy invariance does not establish real-record causality or detector validity.

Before opening that gate, add and pass tests for:

- **Prefix equivalence:** for each decision cutoff, compare streaming features with features from only the signal prefix ending at that cutoff; repeat at varied cutoffs and chunk sizes.
- **Future perturbation:** hold the prefix fixed while replacing, removing, or perturbing all later samples. Previously emitted features and peak timestamps must remain unchanged; no later detection may revise a past decision.
- **Filter/detector state:** verify causal filter state, initialization, warm-up, confirmation latency, chunk-boundary invariance, and deterministic replay. Check that every peak is timestamped by its actual detection/confirmation availability, not retrospectively assigned to an earlier decision.
- **Window and label boundaries:** test half-open/closed sample semantics, exact 5-minute and 30-minute horizon boundaries, 30-second episode inclusion, record-edge censoring, missing/unknown rhythm, and sampling-rate conversions.
- **Outcome isolation:** prove that changing future annotations can change labels but cannot change predictor features, preprocessing state, cohort construction, or per-decision baselines.
- **Real-signal characterization:** after authorized complete waveforms are available, compare cutoff prefixes against full-record processing for diverse noise, rhythm, and boundary cases; review detector failures and feature coverage. Passing synthetic fixtures alone is not an acceptance criterion.

## 7. Data Acquisition Requirements

- For LTAFDB, keep the existing strict validator unchanged. Resolve Record `30` with authoritative PhysioNet/database-maintainer guidance before treating the full catalog as valid; the current candidate exclusion policy is selection-only and not a validator exception.
- Revalidate manifests, headers, annotations, selected records, and available storage immediately before any resumed transfer. The five-record approved scope remains incomplete and has no complete waveforms. Any additional acquisition or AFPDB download requires the appropriate separate authorization; no network transfer was performed for this report.
- For AFPDB, obtain the official v1.0.0 files and preserve its ODC-By attribution and challenge citation. Verify record continuity, subject-set mapping, waveform/header integrity, annotation semantics, and the precise continuation event before defining labels. Retain the original learning/test designation and never use the public test set for tuning.
- Do not redistribute raw ECG in the repository by default. Review license terms, privacy, ethics, and any source-specific use restrictions before public release or linked clinical research. The current local sources contain no authentic paired EHR/wearable data or authorized linkage.

## 8. Recommended Implementation Sequence and Explicit Blockers

**Recommended sequence:** (1) choose whether Phase 2 targets the existing LTAFDB 5–30-minute research question or a separate AFPDB challenge replication; freeze the population, time origin, labels, and split before acquisition; (2) resolve the Record `30` source discrepancy and preserve strict validation; (3) obtain only explicitly approved, complete waveforms and verify file integrity/readability; (4) implement a causal streaming preprocessing/detection contract and pass the tests above; (5) review label/negative eligibility and signal quality on the frozen cohort; (6) establish independent group-based train/validation/test partitions with adequate event and group counts; (7) only then generate features and evaluate the prespecified baselines with cluster uncertainty; (8) keep model outputs out of clinical assessment until external and clinical validation and governance requirements are met.

**Current blockers:**

- Zero complete local LTAFDB `.dat` waveform files; two partial transfers are unusable.
- Record `30` fails the unchanged strict annotation-boundary validation; its source semantics remain unresolved.
- The current label builder may treat a forecast window containing only a sub-30-second AFIB episode as negative; negative-example eligibility needs a documented rule and regression test before feature/model work.
- XQRS whole-record processing has unverified temporal causality; feature extraction and downstream evaluation fail closed.
- No current ECG feature table, trained AF-onset model, out-of-fold predictions, or validated AF performance exists.
- Record IDs do not establish person-level grouping; the approved five-record scope is not an adequate independent evaluation cohort.
- No authentic linked longitudinal EHR/wearable streams or clinical outcomes are present; synthetic fusion is demonstration-only.
- AFPDB is an external candidate for a different, narrow challenge task, not a locally accessible result or a substitute for validating the current target.
- Clinical cardiovascular/AF risk assessment must remain unavailable. No model was trained in Phase 1.

## Sources and Evidence

- Local LTAFDB validation and inventory: `Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/artifacts/data_audit/input_validation.json`, `audit_summary.json`, `record_30_diagnostic.json`, and `work/ltafdb_annotations/waveform_manifest.json`.
- Local research-status evidence: `Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/artifacts/research_readiness/stage12/STAGE12_LICENCE_RESOLUTION.md`, Stage 13/14 acquisition reports, and the project model card.
- Official [LTAFDB v1.0.0](https://physionet.org/content/ltafdb/1.0.0/), [AFPDB v1.0.0](https://physionet.org/content/afpdb/1.0.0/), [AFDB v1.0.0](https://physionet.org/content/afdb/1.0.0/), and [ODC-By v1.0](https://opendatacommons.org/licenses/by/1-0/) pages.

This report records readiness and a proposed research protocol. It is not a clinical validation, legal opinion, acquisition approval, or performance report.
