import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from algorithms import make_dataset, quicksort
from benchmark import run_benchmark


class AlgorithmTests(unittest.TestCase):
    def test_empty_and_single(self):
        for vals in ([], [4]):
            for p in ("first", "random"):
                copy = vals.copy()
                quicksort(copy, pivot=p)
                self.assertEqual(copy, vals)

    def test_patterns(self):
        for kind in ("random", "sorted", "reversed", "identical"):
            for size in (2, 25, 100):
                a = make_dataset(kind, size)
                for pivot in ("first", "random"):
                    b = a.copy()
                    quicksort(b, pivot=pivot)
                    self.assertEqual(b, sorted(a))

    def test_negative_and_duplicates(self):
        values = [4, -3, 0, 4, 4, -1, -3, 9]
        for p in ("first", "random"):
            candidate = values.copy()
            quicksort(candidate, pivot=p)
            self.assertEqual(candidate, sorted(values))

    def test_large_sorted_without_recursion(self):
        values = list(range(2500))
        quicksort(values, pivot="first")
        self.assertEqual(values, list(range(2500)))

    def test_invalid_arguments(self):
        with self.assertRaises(ValueError):
            quicksort([1, 2], pivot="middle")
        with self.assertRaises(ValueError):
            make_dataset("invalid", 10)
        with self.assertRaises(ValueError):
            make_dataset("random", -1)

    def test_benchmark_verifies_and_counts(self):
        rows = run_benchmark((5,), 2, 7)
        self.assertEqual(len(rows), 12)
        self.assertEqual({r["trials"] for r in rows}, {2})
        self.assertTrue(all(r["median_ms"] >= 0 for r in rows))

    def test_seeded_data(self):
        self.assertEqual(make_dataset("random", 60, seed=5), make_dataset("random", 60, seed=5))


if __name__ == "__main__":
    unittest.main()
