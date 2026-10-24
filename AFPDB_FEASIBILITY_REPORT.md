# Atria Twin Phase 2: AFPDB Prediction Dataset Feasibility

**Review date:** 2026-10-22  
**Scope:** Read-only review of the Phase 1 report, existing AF research path, and official PhysioNet AFPDB/challenge materials. Metadata and small-file access checks were performed. No application files were changed, no model was trained, and the full dataset was not downloaded.

## Decision

**C. No defensible model can be implemented with currently accessible data.**

AFPDB is a real and unusually relevant public challenge dataset, not merely an AF detection database. Its published signals are reachable: one full 921,600-byte learning waveform (`p16.dat`) was fetched from PhysioNet's public S3 mirror and then removed from temporary storage; the test waveform `t01.dat` returned HTTP 206 for a one-byte range request. However, this verifies only sample-file retrieval, not a full local cohort. More importantly, the published challenge test labels are not available with the signal files, the historical scoring endpoint did not return a usable page in a metadata request, and the learning set does not identify which two of its 50 record sets share subjects. Consequently, neither faithful held-out challenge scoring nor a leakage-auditable internal validation is presently established.

This is a **data/evaluation blocker**, not a claim that the dataset is scientifically irrelevant or that a model could not be coded. Do not train or report performance until labels and independent evaluation are resolvable. AFPDB is suitable for reconsideration if an authoritative test key/scoring route and learning-set person map (or other defensible group handling) are obtained.

## 1. Existing Atria Twin Boundary

Phase 1 at [`../phase1/DATA_AND_MODEL_READINESS_REPORT.md`](../phase1/DATA_AND_MODEL_READINESS_REPORT.md) and the current code distinguish the following:

| Workstream | Definition and status |
|---|---|
| Existing LTAFDB research pipeline | [`labels.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/labels.py) creates repeated decision points every 5 minutes and a future AFIB-onset target 5–30 minutes ahead, with a 30-minute AF-free lookback. [`features.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/features.py) extracts RR features but blocks on unverified XQRS temporal causality. LTAFDB's local waveforms remain absent and Record 30 remains a strict validation failure. |
| Patient fusion and simulation | [`patient_records.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/patient_records.py) and [`patient_workflow.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/patient_workflow.py) fuse fictional profiles and pass a synthetic baseline into the deterministic demo engine. These features do not enter AF model training. |
| Application workspaces | [`app.py`](../../../Thiranex--Heart-Disease-Prediction-Model-Using-ML-main/atria_twin/app.py) retains five separate workspaces and withholds unavailable/stale research outputs. No app change or AFPDB integration is proposed in this report. |

AFPDB challenge replication, a newly defined rolling 5–30-minute target, and a future-event prediction feature in the existing patient application are different products and evaluation claims. AFPDB's record-pair task cannot be relabeled as the Atria Twin rolling task, and neither is an individual patient's clinical risk estimate.

## 2. Official AFPDB Description, License, and Intended Task

Sources reviewed:

- [PAF Prediction Challenge Database v1.0.0](https://physionet.org/content/afpdb/1.0.0/)
- [Computers in Cardiology Challenge 2001 description](https://physionet.org/content/challenge-2001/1.0.0/)
- [Official event instructions and scoring description](https://physionet.org/content/afpdb/1.0.0/challenge/index.html)
- [Version-specific AFPDB license page](https://physionet.org/content/afpdb/view-license/1.0.0/)
- [ODC Attribution License v1.0](https://opendatacommons.org/licenses/by/1-0/)

PhysioNet labels AFPDB v1.0.0 **Open Access** and links its version-specific license to the **Open Data Commons Attribution License v1.0 (ODC-By)**. The access statement permits anyone to access files subject to the license. Follow dataset and platform citation/attribution terms; this license designation alone does not resolve rights in individual contents, privacy, ethics, or other governance requirements.

The official challenge had two separate events:

- **Event 1, PAF screening:** determine whether a subject belongs to group A (experienced PAF) or group N (no documented AF). Test submissions classify only the odd-numbered record from each subject pair, one of 50 subject classifications.
- **Event 2, PAF prediction:** determine which record in each test pair immediately precedes PAF. Test submissions must designate exactly one record in each pair as `A` (immediately preceding PAF if that subject is in group A) and the other as `N`. The official pair score rewards correctly identifying the pre-onset member for group A subjects; group N contributes a fixed baseline under the original scoring definition. The original competition's test key was withheld during the challenge and scoring used a submission service.

The database page says the learning labels are supplied and the test labels are revealed after the challenge. The challenge results disclose the group counts after the event (28 group-A and 22 group-N test subjects), but that count is not a record-by-record answer key and cannot score a new method. Historical entrant scores are not results for this project.

## 3. Record Structure, Annotations, and Retrieval Evidence

### Published structure

- **Learning set:** 50 record sets, drawn from **48 subjects**. A set has two consecutive 30-minute records and two 5-minute continuation records, all excerpts from one subject's longer ECG. `p*` pairs are from people with PAF; the even-numbered record is immediately before an episode verified in its corresponding continuation, while the odd-numbered record is designated distant (no PAF within 45 minutes before or after the excerpt). `n*` pairs are from people without documented AF; their excerpt times were chosen randomly.
- **Test set:** 50 record sets from 50 different subjects, records `t01` through `t100`, paired consecutively. There are no continuation records in the test set. The challenge page says the test subjects are separate from the learning subjects.
- **Signal:** two ECG channels, 128 samples/second, 16-bit samples, nominal calibration 200 A/D units per mV. Learning 30-minute files contain 230,400 samples/channel; 5-minute continuations contain 38,400 samples/channel. Inspected official headers (`p15`, `p16`, `p15c`, `p16c`, `n01`, `t01`, `t02`) agree with those dimensions and name channels ECG0/ECG1.
- **Annotations:** `.qrs` files are machine-generated and explicitly described by PhysioNet as unaudited and containing errors. They are QRS annotations, not reference rhythm/onset labels. In the training PAF pairs, the dataset's `p` names, odd/even pair convention, and continuation describe the curated onset status. The test waveforms have no continuations; no record-level gold labels were identified in the public listing.
- **Release size:** the official page lists **191.4 MB uncompressed** and a **191.6 MB ZIP**. The page provides recursive `wget` and AWS CLI S3 sync methods.

### Local access and actual retrieval

The workspace has **46 GB free on C:** (`df -h .`, 2026-10-22). This is ample relative to the published 191.4 MB uncompressed release, but the dataset was not bulk downloaded.

Evidence that the source is reachable:

- PhysioNet `HEAD` returned HTTP 200 for `p16.dat` and `t01.dat`, each with `Content-Length: 921600`, and the `RECORDS` catalog with `Content-Length: 1301`.
- Single-byte Range requests for both `p16.dat` and `t01.dat` returned HTTP 206 and one byte.
- A complete `p16.dat` (921,600 bytes) was retrieved from `https://physionet-open.s3.amazonaws.com/afpdb/1.0.0/p16.dat`; a local SHA-256 digest was computed in temporary storage, which was removed. The digest was not verified against a retrieved official checksum entry.
- A full-file request to the PhysioNet web host timed out after 45 seconds at 163,481/921,600 bytes. The S3 mirror's full `p16.dat` transfer succeeded. The official `SHA256SUMS.txt` metadata endpoint responded, but the checksum file was not successfully retrieved and compared.
- No AFPDB files were retained in the project or workspace. Thus **sample-file retrieval is proven, complete-cohort retrieval/integrity is not**.

The challenge page still documents an unofficial scoring route after the competition. A metadata request to the historical scorer URL redirected to HTTPS and ended with HTTP 404 on 2026-10-22. Since no classification was submitted and no POST was attempted, this does not prove the service could never accept submissions by another route; it means a currently working scoring route was not verified. Do not rely on it until confirmed.

## 4. Leakage and Reproduction Fidelity

### Subject grouping

The official dataset states that the 50 learning record sets come from 48 people: therefore two record sets are repeat observations from subjects who occur more than once. Pair membership is clear (adjacent records and continuations), but the inspected headers expose signal metadata only; no stable person ID or explicit mapping between the duplicated record sets was found. A random split of individual 30-minute records would leak within every pair. A split by pair/record set would keep each pair together but could still put the same person's two record sets into different folds. The test split is documented as 50 subjects distinct from learning, but independent re-verification by an identifier is not possible from header fields.

For an original-task reproduction, do not replace the official learning/test split with random record splitting. Keep pairs intact, preserve the original odd/even semantics and test-submission format, and seek an authoritative mapping for the 48 learning subjects before any internal cross-validation. If no mapping exists, report the limitation; do not call pair-level folds subject-disjoint. Do not inspect the hidden test labels or tune against test outputs.

### What can and cannot be reproduced now

The challenge objective and submission rules are documented, and all signal files appear publicly listed. One complete file has been retrieved successfully. The original **training-side task structure** can be reconstructed from the named learning records and their continuations. However, faithful **held-out test scoring** is not currently reproducible from verified local evidence: no record-by-record test answer key has been found, and the documented historical scorer did not respond successfully to the metadata probe. No training/validation/test result can therefore be reported here.

The accessible challenge material may support a future controlled replication if the full archive is acquired and validated, the hidden-label scoring path/key is resolved, and the learning-subject duplicates are handled without leakage. The existing 2026 challenge result tables are historical comparisons only, not a substitute for a new baseline's independent score.

## 5. Three Non-Interchangeable Tasks

| Task | Prediction unit and target | AFPDB feasibility |
|---|---|---|
| **Original challenge reproduction** | A 30-minute record at its end; Event 1 predicts group A vs N, or Event 2 selects the imminent-PAF member of each test pair. Learning/test organization and pair scoring are fixed by the challenge. | Closest scientific fit. Full sample retrieval works, but no verified test key/scorer or learning duplicate-subject map is available. Exact external evaluation is blocked. |
| **New rolling 5–30-minute AF-onset task** | Repeated time points, with only ECG observed by each time `t` predicting a future annotated AF onset in `[t+5m, t+30m]`, a clean past lookback, and fully observed future labels. | Not supported by the curated excerpts as published. The learning set's distant/precursor labels are record-level challenge categories, not labels for every rolling decision. Continuations are only 5 minutes and are absent for test records; `.qrs` files are not rhythm-onset annotations. This target would require a different longitudinally annotated dataset/protocol. |
| **Future-event feature in Atria Twin** | A patient-specific output using authorized linked patient data and a defined clinical outcome/horizon, evaluated for the intended population and use. | Not supported. AFPDB records have no linkage to the synthetic `DEMO-AT-*` patients, EHR, or wearable data. Challenge scores cannot be presented as individual patient risk. Integration is out of scope and clinical risk remains unavailable. |

## 6. Smallest Baseline Experiment: Specification, Not Execution

If the remaining data/evaluation blockers are resolved, the smallest scientifically aligned baseline would be a **locked Event 2 record-pair experiment**, not an Atria Twin rolling model:

1. Acquire and hash-verify the official complete AFPDB release. Preserve the supplied learning/test assignment and all pair/continuation relationships. Confirm each signal sample count against its WFDB header. Do not use the challenge test set for fitting, feature selection, or tuning.
2. Use learning PAF pairs only for the precursor-vs-distant model. Define the prediction time as the end of each 30-minute excerpt. Treat the entire excerpt as historical input available at that time; do not read its continuation for predictors. Preserve the 5-minute continuation as the source-designated follow-on excerpt for reviewing the training convention, but do not claim machine-verifiable rhythm onset from it: the release documents `.qrs` beat detections, not audited rhythm labels. Exclude the unaudited `.qrs` marks as ground-truth features/labels; detect QRS from the two ECG leads or use an independently validated detector.
3. Predeclare two-lead ECG conversion from header calibration, quality checks, and handling of flat/clipped/missing segments. For a simple baseline, derive per-lead mean HR, SDNN, RMSSD, and pNN50 from detected beats over the 30-minute excerpt. Include lead identity/aggregation explicitly; do not tune features on test records. Any filter/detector must use only samples in that 30-minute input. The prediction timestamp is after the excerpt, so its full-window features are historical for this specific task, but this does not establish a rolling real-time detector.
4. Fit a regularized logistic classifier to distinguish the even-numbered immediately pre-onset `p` excerpt from its odd-numbered distant `p` mate, using learning PAF pairs. Fit scaling/imputation within training partitions only. Evaluate pairwise ranking: select the higher imminent-PAF score within each held-out PAF pair. This is a minimal Event 2 research baseline, not a reproduction of Event 1 and not sufficient to score the mixed, unlabeled test set by itself.
5. For internal development, use subject-grouped folds only if the repeated-subject mapping among 48 learning subjects is obtained. Otherwise, no pair-level random CV may be represented as independent-subject validation. Lock the model and decision rule using learning data before applying them once to the official test pairs.
6. For original Event 2 scoring, generate exactly one `A` and one `N` per test pair as specified. Report the original pair score only with a verified official key/scorer. If scoring remains unavailable, report predictions as unscored and do not invent accuracy. Event 1 would require its own separately declared subject-level screening baseline and official score; do not merge both metrics.

Required reporting, after blockers resolve: number of usable subject groups/pairs and signal exclusions; Event 2 correctly identified PAF pairs and the original score definition; Event 1 subject accuracy only if separately implemented; confidence intervals by independent subject (not individual windows); fixed split/version/hash provenance; and failure/missing-feature counts. Because the challenge test contains 50 subjects, interval estimates will be imprecise. Do not claim calibration or clinical utility from challenge accuracy.

## 7. Required Tests and Gates

- **Acquisition/integrity:** all catalog entries expected for the release are present; every waveform's actual byte count matches listing/official checksums; WFDB headers parse; signal sample count, channels, 128 Hz, calibration, and duration agree; no truncated files or silent partials are accepted.
- **Pair/subject grouping:** verify all pair mates and learning continuations; assert that no pair crosses a partition; once a person mapping is available, assert zero subject overlap across train/validation/test, including duplicate record sets. Test submission output has exactly 50 Event 1 entries or exactly one `A` per each of 50 Event 2 pairs.
- **Label semantics:** tests for p odd/even ordering, continuation-to-onset relation, distant-window stated margins, control interpretation, and historical test key alignment. Unknown or missing event labels must remain unknown, not negative.
- **Signal preprocessing:** tests for header-based physical scaling, channel order, malformed/truncated inputs, flat segments, missing data, reproducible detector output, and feature-window bounds. QRS annotations are not trusted as ground truth because the source says they are unaudited.
- **Leakage:** test that no continuation/test data is read during fitting, no train/test pair or subject overlap occurs, and all learned preprocessing parameters are fitted only on training partitions. Assert that labels and subject identity are excluded from predictors.
- **Task boundary:** tests should make it impossible to reuse AFPDB pair labels as the existing LTAFDB rolling label or to expose challenge scores as patient-level risk in the application.

These are requirements for a future implementation; none was executed as a model experiment in Phase 2.

## 8. Remaining Blockers and Recommendation

- Full AFPDB release is not local. The official page lists 191.4 MB uncompressed and the C: volume has 46 GB free, but only one complete learning waveform and one-byte test access were verified. The PhysioNet full-file route was slow; S3 worked for `p16.dat`.
- The local full-release manifest/checksum validation has not been performed. The p16 local SHA-256 was calculated, but not compared with a successfully retrieved official checksum entry.
- Test labels are not found in the public signal listing/headers; the official results disclose aggregate class counts, not the per-record answer key. A currently working official scorer was not verified (historical endpoint metadata returned 404).
- Learning set has 50 record sets from 48 subjects; identities for the duplicated subjects are not mapped in inspected headers/docs. Pair grouping alone is insufficient to certify subject-independent internal CV.
- `.qrs` files are unaudited beat detections, not rhythm annotations. The PAF target rests on challenge curation/continuation convention and must be independently mapped for the training examples.
- AFPDB's target is not the Atria Twin rolling 5–30-minute label and has no patient/EHR/wearable linkage. App integration and clinical risk inference remain unsupported.
- Existing LTAFDB Record 30 validation and XQRS causality gates remain unchanged and blocking for that separate rolling-target research route.

**Recommendation:** do not train or integrate a model yet. First obtain a reliable answer-key/scoring route and an authoritative learning-set subject mapping; then acquire and integrity-check the full AFPDB release using the disclosed 191.4 MB size and current free-space evidence, and run only the predeclared challenge-aligned baseline. If those sources cannot be established, retain the current unavailable-risk state and select a different dataset with explicit longitudinal onset labels, subject IDs, and an accessible independent test key.

**Final conclusion: C. No defensible model can be implemented with currently accessible data.**

This report is a feasibility assessment, not an acquisition approval, model result, clinical validation, or legal opinion.
