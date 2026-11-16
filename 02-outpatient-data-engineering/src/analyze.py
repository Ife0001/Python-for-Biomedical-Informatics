"""Outpatient encounter data engineering (BMI 5007 portfolio adaptation).

Input is a CSV with pseudonymous patient/visit keys, physician fields and
ICD-9 codes. Each patient/visit can span multiple source rows.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

PHYSICIAN_FIELDS = ("Primary_Physician", "Operating_Physician", "Other_Physician")
DIAGNOSIS_FIELDS = tuple(f"ICD9_DGNS_CD_{i}" for i in range(1, 11))
REQUIRED = ("Patient_ID", "Visit_ID") + PHYSICIAN_FIELDS + DIAGNOSIS_FIELDS


def normalize(value: str | None) -> str:
    return (value or "").strip()


def analyze_file(source: Path) -> tuple[list[dict[str, object]], dict[str, object], Counter[int]]:
    """Return per-patient summaries, dataset quality metrics and visit histogram.

    Diagnostic frequency means number of *distinct visits* on which a code
    appears, not number of duplicate row mentions. The visit's code set is the
    union of codes recorded across all of its rows.
    """
    visits: dict[tuple[str, str], dict[str, object]] = {}
    row_total = 0
    missing_patient = missing_visit = 0
    diagnosis_mentions = 0
    rows_with_no_diagnoses = 0
    with source.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("The CSV is empty or lacks a header")
        missing_columns = sorted(set(REQUIRED) - set(reader.fieldnames))
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        for row_total, row in enumerate(reader, start=1):
            patient = normalize(row["Patient_ID"])
            visit = normalize(row["Visit_ID"])
            if not patient:
                missing_patient += 1
            if not visit:
                missing_visit += 1
            # Invalid keys cannot safely be assigned to a unique encounter.
            if not patient or not visit:
                continue
            key = (patient, visit)
            if key not in visits:
                visits[key] = {"physicians": set(), "diagnoses": set(), "source_rows": 0}
            v = visits[key]
            v["source_rows"] += 1
            v["physicians"].update(p for f in PHYSICIAN_FIELDS if (p := normalize(row[f])))
            codes = {d for f in DIAGNOSIS_FIELDS if (d := normalize(row[f]))}
            diagnosis_mentions += sum(bool(normalize(row[f])) for f in DIAGNOSIS_FIELDS)
            if not codes:
                rows_with_no_diagnoses += 1
            v["diagnoses"].update(codes)

    patients: dict[str, dict[str, object]] = defaultdict(
        lambda: {"visit_ids": set(), "physicians": set(), "diagnosis_visit_counts": Counter()}
    )
    for (patient, visit), values in visits.items():
        p = patients[patient]
        p["visit_ids"].add(visit)
        p["physicians"].update(values["physicians"])
        p["diagnosis_visit_counts"].update(values["diagnoses"])

    summaries: list[dict[str, object]] = []
    histogram: Counter[int] = Counter()
    for patient, p in sorted(patients.items()):
        counts: Counter[str] = p["diagnosis_visit_counts"]
        most_common = min((code for code, count in counts.items() if count == max(counts.values())), default="")
        total_visits = len(p["visit_ids"])
        histogram[total_visits] += 1
        summaries.append({
            "Patient_ID": patient,
            "Total_Visits": total_visits,
            "Total_Physicians": len(p["physicians"]),
            "Total_Diagnosis": len(counts),
            "Most_Freq_Diagnosis": most_common,
        })

    repeated_visits = sum(v["source_rows"] > 1 for v in visits.values())
    stats: dict[str, object] = {
        "source_rows": row_total,
        "rows_skipped_missing_patient_id": missing_patient,
        "rows_skipped_missing_visit_id": missing_visit,
        "unique_patients": len(patients),
        "unique_patient_visit_pairs": len(visits),
        "patient_visit_pairs_with_multiple_rows": repeated_visits,
        "additional_rows_for_existing_patient_visit_pairs": sum(v["source_rows"] - 1 for v in visits.values()),
        "source_rows_without_diagnosis_codes": rows_with_no_diagnoses,
        "diagnosis_code_mentions_in_source_rows": diagnosis_mentions,
        "diagnosis_code_mentions_on_distinct_visits": sum(len(v["diagnoses"]) for v in visits.values()),
        "notes": [
            "Rows with the same patient and visit identifier are consolidated by union of physician and diagnosis values.",
            "Diagnosis frequency is calculated over distinct visits; tied codes use ascending lexical order.",
            "These metrics describe dataset structure only, not clinical outcomes or causal effects.",
        ],
    }
    return summaries, stats, histogram


def save_results(summaries: list[dict[str, object]], stats: dict[str, object],
                 histogram: Counter[int], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    # Contains patient-linked identifiers: NEVER commit or share without authorization.
    with (output / "patient_summary_PRIVATE.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Patient_ID", "Total_Visits", "Total_Physicians", "Total_Diagnosis", "Most_Freq_Diagnosis"])
        writer.writeheader()
        writer.writerows(summaries)
    (output / "data_quality_report.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    with (output / "visit_count_distribution.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["unique_visits_per_patient", "number_of_patients"])
        for visits, number in sorted(histogram.items()):
            writer.writerow([visits, number])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/outpatient_sample.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    summaries, stats, histogram = analyze_file(args.input)
    save_results(summaries, stats, histogram, args.output)
    print(json.dumps({k: v for k, v in stats.items() if k != "notes"}, indent=2))
    print(f"Saved 3 output files to {args.output}. Outputs include patient-linked data: do not publish.")


if __name__ == "__main__":
    main()
