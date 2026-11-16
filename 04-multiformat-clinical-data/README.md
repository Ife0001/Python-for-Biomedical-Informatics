# Multi-Format Clinical Data Processing: CSV, JSON, and XML

**Python standard library · CSV · JSON · XML · Schema validation · Data quality · Descriptive statistics**

## Healthcare data question

How can heterogeneous clinical measurement datasets be read, validated, and summarized consistently **without falsely treating them as a linked patient cohort**?

This independent portfolio adaptation builds on CSV, JSON, and XML exercises from BMI 5007. The three inputs are **distinct educational datasets** with different structures; shared-looking `DataID` values are not evidence of a common person. Original assignment scripts and templates are not published as project source code.

## Analyses

| Format | Input structure | Output | Meaning |
| --- | --- | --- | --- |
| CSV | `DataID, Glucose, Location, Group` | `glucose_by_csv_group.csv` | Mean glucose by supplied group label |
| JSON | `Data.Dataset` records with `DataID`, `BMI`, `Glucose` | `glucose_by_bmi_group.csv` | Mean glucose across BMI ranges |
| XML | `<data><dataset>` with `DataID`, `BP_Before`, `BP_After`, `Location` | `bp_difference_by_location.csv` | Mean before-minus-after blood pressure by location |

BMI ranges are defined as below 18.5, 18.5 to below 25, 25 to below 30, and 30 or higher. These are **categorization cutoffs**, not diagnoses. The BP difference is the numerical change recorded in the XML; the data do not establish causality or treatment effectiveness. Units and measurement procedures should be confirmed from original source metadata before clinical interpretation.

## Run locally (Python 3.10+; no external packages)

From inside this project directory:

```cmd
python -m unittest discover -s tests -v
python src/generate_demo.py
python src/analyze.py
```

The demo generator writes three **fictional** input files to `data/`, then analysis creates four results in `outputs/` (three CSV tables and a JSON report). These directories are excluded from Git publication.

To analyze the original source files locally instead, place them in `data/` with the expected names. Or run:

```cmd
python src/analyze.py --csv "path/to/csv_final_1.csv" --json "path/to/json_final_1.json" --xml "path/to/xml_final_2.xml"
```

## Validation and quality rules

- All expected source columns/fields are required; absent fields raise readable errors.
- Required IDs and analytical grouping keys cannot be blank.
- Numeric conversions reject nonnumeric, NaN, and infinite values.
- Input records are counted and distinct DataIDs reported **within each individual file**.
- Mean estimates are accompanied by group counts and rounded to two decimals.
- The tool does **not** merge files or assert patient identity across sources.
- Explicit invalid records result in a failure instead of silent row removal.

## Repository structure

```text
04-multiformat-clinical-data/
├── README.md
├── .gitignore
├── data/.gitkeep
├── outputs/.gitkeep
├── figures/.gitkeep
├── src/analyze.py
├── src/generate_demo.py
└── tests/test_analyze.py
```

## Privacy and limitations

Only code, documentation, tests, and folder placeholders should be pushed to GitHub. The original educational datasets and generated results are locally excluded by `.gitignore` until their provenance and sharing terms are verified. The supplied original CSV/JSON/XML datasets have separate samples and may have different measurement settings, sizes, and meanings; comparisons across those datasets are **not** valid patient-level comparisons.
