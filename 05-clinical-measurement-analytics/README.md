# Clinical Measurement Analytics and Data Quality with Pandas

**Python · Pandas · Clinical measurement validation · Missingness · Descriptive analytics**

## Healthcare informatics question
How do missing, implausible, and duplicate records affect descriptive summaries of clinical measurements? This standalone project illustrates a reproducible *data-quality-first* workflow using **fictional records**. It is not a clinical study, a treatment-effect analysis, or a screening tool.

## What this project does
1. Generates deterministic **synthetic** measurement records containing BMI, glucose (mg/dL), and systolic/diastolic blood pressure measurements before and after a fictional observation point.
2. Validates the required dataset schema; detects exact duplicates and conflicting repeated record identifiers.
3. Converts measurement strings to numeric values and marks missing/invalid values appropriately rather than replacing them with zero.
4. Masks values outside **illustrative technical plausibility bounds**, documenting counts in a JSON quality report. These bounds are not clinical reference intervals.
5. Applies conventional BMI categories and produces aggregate descriptive summaries of glucose and paired blood pressure *differences* by synthetic group. A negative difference means the later value is lower; no causality is inferred.
6. Exports four aggregate summary reports (no record-level identifiers).

## Relationship to the BMI 5007 coursework
This independent portfolio adaptation draws on prior exercises using Pandas and clinical measurement fields (glucose, BMI, and blood pressure) in CSV, JSON, and XML. Unlike Project 04 (format parsing), Project 05 emphasizes **missingness, measurement validation, duplicate detection, categorical analysis, and reproducible quality reporting**. Original assignment code and datasets are not republished here, and data from distinct course exercises are **not linked as if from the same patients**.

## Folder layout
```
05-clinical-measurement-analytics/
├── src/
│   ├── generate_demo.py
│   └── analyze.py
├── tests/test_analyze.py
├── data/.gitkeep
├── outputs/.gitkeep
├── figures/.gitkeep
├── requirements.txt
└── .gitignore
```

## Run locally
From the Project 05 folder, run these commands separately:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/generate_demo.py
python src/analyze.py
```

The last two commands generate `data/synthetic_measurements.csv` and four outputs:
- `outputs/measurements_by_group.csv`
- `outputs/glucose_by_bmi_category.csv`
- `outputs/measurement_missingness.csv`
- `outputs/quality_report.json`

All data files and outputs are ignored by Git by default. The generator lets anyone regenerate example records without distributing record-level files.

## Analytic limitations
- The dataset is intentionally synthetic, so estimates have **no population or clinical generalizability**.
- BMI category cutoffs are descriptive groupings, not individualized medical advice.
- Blood pressure differences are arithmetic comparisons, **not** evidence of intervention benefit or causation.
- Technical plausibility thresholds are intentionally broad and not universal data-validation standards.
- Exact duplicate rows are removed. Conflicting duplicate IDs trigger an error instead of silent deduplication.
- A real deployment would additionally require source provenance, units validation, encounter timestamps, appropriate coding conventions, governance review, and broader testing.
