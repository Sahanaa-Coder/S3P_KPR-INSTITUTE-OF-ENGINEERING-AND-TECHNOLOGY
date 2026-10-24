# AtriaTwin — Build Specification

## Product goal

Build a software-only proof of concept for a patient-specific cardiovascular digital twin that explores short-horizon atrial-fibrillation (AF) onset forecasting in ambulatory ECG recordings. It is a research demonstration, not a diagnostic or treatment tool.

## Current implemented fallback

The current dashboard adds a reproducible UCI classifier for the bundled dataset's existing `num > 0` prevalent-disease label and displays its held-out output beside a separate, clearly fictional HR/RMSSD replay. The replay is not linked to the UCI record or used as model input. No complete LTAFDB `.dat` waveform is present, so real ECG time-series analysis and AF-onset prediction remain unavailable; the current fallback does not satisfy the future-event forecasting goal below.

## Challenge fit

- **Condition:** known paroxysmal AF; do not claim general-population screening.
- **Dynamic stream:** open, annotated ambulatory ECG, replayed as a time series.
- **Static stream:** synthetic clinical profile, explicitly marked synthetic. It must not be represented as patient-linked EHR data. A separate simulation mode will demonstrate how a static profile initializes the twin's prior/state and how ECG updates that state. It will be labeled as simulated and excluded from real-data performance claims.
- **Primary target:** an annotated AFIB interval lasting at least 30 seconds begins 5–30 minutes after a clean decision point, only after a data audit confirms enough usable pre-onset examples. Exclude windows with AF already present, recent AF in the lookback, or insufficient known rhythm history.
- **Evaluation:** split by person if the dataset documents person IDs; otherwise keep all windows from each recording together and clearly report recording-level rather than patient-level evaluation. Compare against a clearly labeled retrospective annotation-history reference, training-prevalence baseline, and ECG signal baselines. The annotation-history reference is an offline comparator, not an online input. Report event-level sensitivity, false alerts per patient-day/recording-day, lead time, and uncertainty; do not rely on accuracy alone.
- **Hardware:** none required. The demo replays stored open data and synthetic context.

## Data gate before model claims

1. Inspect the official dataset terms and cite the dataset correctly.
2. Download a small, documented subset first; do not check raw ECG into GitHub.
3. Count people, recordings, AF episodes, and usable forecast windows after exclusions.
4. If the 30-minute forecast target has too few usable onsets, use the PAF prediction challenge as a small benchmark replication or narrow the claim. Do not silently change the target or manufacture real-data labels.
5. Keep synthetic data separate from real-data evaluation and mark every synthetic field in the UI and exported files.

## MVP architecture

```text
Public ambulatory ECG + annotations
        ↓
Signal quality checks → QRS/RR feature extraction
        ↓
Per-record baseline from past data only → grouped baseline/model comparison
        ↓
Uncalibrated research score trace + fixed operating points
(calibration is a separate evidence gate)
        ↓
Streamlit clinician dashboard with replay, timeline, uncertainty, and limitations

Synthetic clinical profile ─────────────→ synthetic baseline seed in simulation only
```

In the simulated clinic only, the queue demonstrates a one-sided CUSUM over synthetic HR increases and RMSSD decreases relative to the seeded baseline. It uses fixed illustrative scales (8 bpm and 10 ms), a 1.0 per-step allowance, and display cutoffs at 1.0 and 4.0. These are interface-demo settings; they have not been fitted to or evaluated against AF outcomes and must never be shown as clinical alert thresholds. The LTAFDB research view remains a separate ECG-only evaluation path.

The static profile must remain visibly distinguishable from real ECG-derived evidence unless a genuinely paired dataset becomes available. Do not claim that synthetic EHR fusion improves prediction. The demo must show both streams entering the twin state, while the AF forecasting evaluation must report that it is based on real ECG only.

## Tool roles

- **Codex:** implement the shared specification, data pipeline, model, dashboard, and reproducible documentation in the repository.
- **VS Code:** primary editor and local run/debug surface.
- **Claude:** independent design/code review and challenge-jury critique; it does not overwrite the source of truth.
- **Kiro:** maintain requirements, acceptance criteria, and implementation tasks derived from this specification.
- **Antigravity:** optional isolated implementation/review work; avoid concurrent edits to the same files.
- **Stitch:** produce a dashboard visual reference; translate the selected design into the Streamlit app.
- **Supabase:** defer unless persistence or a hosted demo is needed. If used, store only synthetic demo profiles and non-sensitive run metadata.
- **Groq:** defer for MVP. If later used, only turn model-produced structured facts into optional plain-language summaries; never let an LLM calculate risk, create labels, or recommend treatment.

## Delivery stages

1. **Feasibility:** confirm the dataset license, local tooling, label conventions, and usable onset count.
2. **Data pipeline:** reproducible download instructions, signal quality checks, feature extraction, and patient/time splits.
3. **Baselines:** prevalence, time-since-last-event, and simple ECG feature models; report failure cases.
4. **Twin state:** patient-specific rolling baseline and drift features using past-only data.
5. **Dashboard:** clinic queue, one-patient replay, event timeline, alert rationale, and explicit synthetic-data labels.
6. **Submission:** model/data cards, architecture diagram, public README, presentation, and 20-minute demo video.

## Safety and honesty rules

- No diagnosis, treatment, medication, or dose recommendations.
- No claim of clinical validation, wearable validation, Indian-population validation, or stroke prevention.
- Show false alerts, missed events, limitations, and the selected cohort.
- Do not use real personal data or put raw ECG files in the public repository.
