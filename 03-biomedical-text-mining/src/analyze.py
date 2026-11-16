"""Biomedical document-level term statistics and simple phrase screening.

Standard-library only. The screening rules are lexical and NOT clinical NLP or
medical concept extraction. Source documents stay local by default.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?", re.I)
# This is a screening pattern, not a semantic follow-up action classifier.
FOLLOWUP_RE = re.compile(r"\b(?:follow[\s-]?up|f\s*/\s*u)\b", re.I)


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.casefold())


def analyze_documents(directory: Path, term: str = "diabetes") -> tuple[list[dict], Counter]:
    if not directory.is_dir():
        raise FileNotFoundError(f"Input directory not found: {directory}")
    files = sorted(directory.glob("*.txt"))
    # Some coursework archives contain readme.md.txt, not a document.
    files = [p for p in files if p.name.casefold() != "readme.md.txt"]
    if not files:
        raise ValueError(f"No .txt documents in {directory}")
    all_words: Counter = Counter()
    records = []
    for path in files:
        text = path.read_text(encoding="utf-8-sig")
        words = tokenize(text)
        counts = Counter(words)
        all_words.update(counts)
        records.append({
            "document": path.name,
            "tokens": len(words),
            "unique_terms": len(counts),
            "term_mentions": counts[term.casefold()],
            "followup_phrase_mentions": len(FOLLOWUP_RE.findall(text)),
            "contains_followup_phrase": int(bool(FOLLOWUP_RE.search(text))),
        })
    return records, all_words


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/demo_texts"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    parser.add_argument("--term", default="diabetes", help="Single token to count across documents")
    parser.add_argument("--top", type=int, default=15, help="Number of top terms to export")
    parser.add_argument("--private", action="store_true", help="Indicates real/local input; write only aggregate outputs, no filenames")
    args = parser.parse_args()
    if len(tokenize(args.term)) != 1 or tokenize(args.term)[0] != args.term.casefold():
        parser.error("--term must be a single simple token")
    if args.top < 1:
        parser.error("--top must be positive")
    rows, word_counts = analyze_documents(args.input, args.term)
    args.output.mkdir(parents=True, exist_ok=True)
    # For real/local corpora, do not export filenames or per-document statistics.
    if not args.private:
        write_csv(args.output / "document_summary.csv", rows, list(rows[0]))
    else:
        (args.output / "document_summary.csv").unlink(missing_ok=True)
    top = [{"term": w, "mentions": c} for w, c in sorted(word_counts.items(), key=lambda v: (-v[1], v[0]))[:args.top]]
    write_csv(args.output / "top_terms.csv", top, ["term", "mentions"])
    summary = {
        "documents": len(rows),
        "tokens": sum(x["tokens"] for x in rows),
        "distinct_terms": len(word_counts),
        "target_term": args.term,
        "target_term_mentions": sum(x["term_mentions"] for x in rows),
        "documents_with_target_term": sum(x["term_mentions"] > 0 for x in rows),
        "documents_with_followup_phrase": sum(x["contains_followup_phrase"] for x in rows),
        "followup_phrase_mentions": sum(x["followup_phrase_mentions"] for x in rows),
        "method": "case-insensitive lexical counts; no stemming, negation or clinical semantics",
        "privacy_mode": "aggregate_only" if args.private else "demo_document_details",
    }
    (args.output / "corpus_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Saved aggregate results to {args.output}")


if __name__ == "__main__":
    main()
