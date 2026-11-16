# Project 02 — Patient-Level Outpatient Encounter Processing and Data Quality

**Python · CSV · Dictionaries and Sets · Encounter Consolidation · Healthcare Data Quality**

## Purpose

Transform rows from a sample outpatient claims-style dataset into consistent patient-level summaries, while making repeated patient–visit records and data quality issues explicit. This is a standalone portfolio adaptation of a BMI 5007 programming exercise; the original coursework files and template are kept separate.

## Dataset and scope

The original uploaded sample is `outpatient_sample.csv`, with `Patient_ID`, `Visit_ID`, three physician identifier columns and ten ICD-9 diagnosis fields. It has **250 source rows** and **15 columns**. It contains repeated rows for some patient–visit pairs. These are **not exact duplicate records**: some contain different physicians or diagnosis codes and should not be discarded indiscriminately.

**Privacy and release status:** The identifiers are formatted as pseudonymous codes, but pseudonymization does not establish that a dataset is public or safe to share. The source's provenance, permissions, and any re-identification risks have not been established. **Do not push the input CSV, patient-level outputs, or generated reports to a public repository.** This project deliberately excludes all input and output data from Git by default.

## Analytical approach

1. Validate that the expected 15 columns exist and preserve all ID/ICD fields as strings.
2. Skip rows with blank patient or visit identifiers and count those records as data-quality issues.
3. Consolidate rows by `(Patient_ID, Visit_ID)`, unioning all physician IDs and diagnosis codes reported on that visit.
4. For each patient, count **distinct visits**, **distinct physicians**, and **distinct diagnosis codes**.
5. Define most frequent diagnosis as the code recorded on the greatest number of **distinct visits**, rather than repeated appearances in source rows. Ties are resolved by ascending code order.
6. Produce patient-level summaries (private by default), dataset-quality checks, and a distribution of unique visits per patient.

This is descriptive data engineering, not disease prevalence estimation, clinical prediction, or evidence of clinician performance.

## Files

```text
02-outpatient-original-adaptation/
├── README.md
├── .gitignore
├── data/                # local source CSV; ignored by Git
├── src/
│   └── analyze.py
├── tests/
│   └── test_analyze.py
├── outputs/             # private derived files; ignored by Git
└── figures/             # reserved for future approved figures
```

## Run locally

Python 3.10+ is required; the project uses only the Python standard library.

From the Project 02 folder:

```sh
python -m unittest discover -s tests -v
python src/analyze.py --input data/outpatient_sample.csv --output outputs
```

The second command requires an authorized local copy of the original CSV placed at `data/outpatient_sample.csv`. Files generated in `outputs/` include a patient-linked `patient_summary_PRIVATE.csv`, `data_quality_report.json`, and `visit_count_distribution.csv`. Do not upload these without a separate disclosure assessment.

## Key design decisions and limitations

- Multiple rows with the same patient–visit key are merged **for analysis**, not blindly deleted. The script retains no sequence information and cannot determine whether code entries were revised versus cumulatively recorded.
- Diagnosis code frequency is operationalized as number of unique visits containing the code. This differs from the raw source's occurrence count and should be reported explicitly.
- `Patient_ID` is a record-linkage key and `Visit_ID` is an encounter identifier; neither implies personal identity validation.
- ICD-9 codes are preserved as uninterpreted text. Clinical interpretation would require a validated reference code system, version/date information, and domain review.
- No demographic, clinical outcome, or date information is present in the provided sample; avoid inventing clinic, age, sex, wait time, or temporal analyses.
- The small excerpt and unknown sampling frame do not support inference to a population.

## Skills demonstrated

Data ingestion and validation · schema contracts · entity/encounter grain · reconciliation of repeated records · deduplication logic · Python sets and dictionaries · counters · deterministic reporting · automated tests · confidentiality-aware data publishing.
