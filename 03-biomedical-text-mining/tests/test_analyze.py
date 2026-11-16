import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from analyze import analyze_documents, tokenize, FOLLOWUP_RE


class TextAnalysisTests(unittest.TestCase):
    def test_tokenization(self):
        self.assertEqual(tokenize("Diabetes, DIABETES; f/u"), ["diabetes", "diabetes", "f", "u"])

    def test_followup_variations(self):
        for phrase in ("follow-up", "follow up", "followup", "f/u", "F / U"):
            with self.subTest(phrase=phrase):
                self.assertIsNotNone(FOLLOWUP_RE.search(phrase))

    def test_counts_and_readme_exclusion(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'a.txt').write_text('Diabetes diabetes. Follow-up; f/u.', encoding='utf-8')
            (root / 'b.txt').write_text('No diabetes documented.', encoding='utf-8')
            (root / 'readme.md.txt').write_text('diabetes ' * 20)
            rows, counter = analyze_documents(root)
            self.assertEqual(len(rows), 2)
            self.assertEqual(counter['diabetes'], 3)
            self.assertEqual(rows[0]['followup_phrase_mentions'], 2)

    def test_missing_input(self):
        with self.assertRaises(FileNotFoundError):
            analyze_documents(Path('/no-such-input-for-project-03'))


if __name__ == '__main__':
    unittest.main()
