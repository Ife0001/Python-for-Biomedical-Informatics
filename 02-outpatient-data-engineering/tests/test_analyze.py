"""Tiny synthetic fixtures validate consolidation, code counting and missing-key handling."""
import csv
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analyze import analyze_file, REQUIRED


class OutpatientTests(unittest.TestCase):
    def test_multiline_encounter_is_not_multiple_visits(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "test.csv"
            def row(p, v, physician, *codes):
                r = {k: "" for k in REQUIRED}
                r.update(Patient_ID=p, Visit_ID=v, Primary_Physician=physician)
                for i, code in enumerate(codes, 1):
                    r[f"ICD9_DGNS_CD_{i}"] = code
                return r
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=REQUIRED)
                writer.writeheader()
                writer.writerows([
                    row("P1", "V1", "DR1", "4019", "25000"),
                    row("P1", "V1", "DR2", "4019", "2724"),
                    row("P1", "V2", "DR1", "25000"),
                    row("P2", "V3", "DR3", "V5841"),
                    row("", "V4", "DR3", "4019"),
                ])
            summaries, stats, hist = analyze_file(path)
            by_id = {s["Patient_ID"]: s for s in summaries}
            self.assertEqual((stats["source_rows"], stats["unique_patient_visit_pairs"]), (5, 3))
            self.assertEqual(stats["patient_visit_pairs_with_multiple_rows"], 1)
            self.assertEqual(stats["rows_skipped_missing_patient_id"], 1)
            self.assertEqual(by_id["P1"]["Total_Visits"], 2)
            self.assertEqual(by_id["P1"]["Total_Physicians"], 2)
            self.assertEqual(by_id["P1"]["Total_Diagnosis"], 3)
            self.assertEqual(by_id["P1"]["Most_Freq_Diagnosis"], "25000")
            self.assertEqual(sum(hist.values()), 2)

    def test_rejects_missing_schema(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.csv"
            path.write_text("Patient_ID,Visit_ID\nP1,V1\n")
            with self.assertRaisesRegex(ValueError, "Missing required columns"):
                analyze_file(path)


if __name__ == "__main__":
    unittest.main()
