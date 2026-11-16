"""Format-aware analysis of three independent, educational healthcare datasets.

CSV  : mean glucose by Group.
JSON : mean glucose by conventional BMI *ranges* (not diagnoses).
XML  : mean systolic BP difference (before minus after) by Location.

The source datasets are not linked by DataID and are not combined at patient level.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
import statistics
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_CSV = {'DataID','Glucose','Location','Group'}
REQUIRED_JSON = {'DataID','BMI','Glucose'}
REQUIRED_XML = {'DataID','BP_Before','BP_After','Location'}


def numeric(raw, field, row):
    try:
        val = float(str(raw).strip())
        if not __import__('math').isfinite(val):
            raise ValueError
        return val
    except (TypeError, ValueError):
        raise ValueError(f'Invalid {field} in row {row}: {raw!r}') from None


def summarize(values):
    return [{'group': str(group), 'n': len(nums), 'mean': round(statistics.mean(nums), 2)}
            for group, nums in sorted(values.items())]


def read_csv(path):
    groups = defaultdict(list)
    ids = set()
    with Path(path).open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not REQUIRED_CSV.issubset(reader.fieldnames):
            raise ValueError('CSV missing required columns: ' + ', '.join(sorted(REQUIRED_CSV - set(reader.fieldnames or []))))
        for line, row in enumerate(reader, 2):
            if not row['DataID'] or not row['Group']:
                raise ValueError(f'CSV missing DataID or Group at line {line}')
            ids.add(row['DataID'])
            glucose = numeric(row['Glucose'], 'Glucose', line)
            groups[row['Group'].strip()].append(glucose)
    if not groups:
        raise ValueError('CSV contains no observations')
    return summarize(groups), {'rows': sum(map(len, groups.values())), 'distinct_data_ids':len(ids)}


def bmi_group(bmi):
    if bmi < 0:
        raise ValueError('BMI must not be negative')
    if bmi < 18.5:
        return 'Under 18.5'
    if bmi < 25:
        return '18.5–24.9'
    if bmi < 30:
        return '25.0–29.9'
    return '30.0 or higher'


def read_json(path):
    with Path(path).open(encoding='utf-8-sig') as f:
        data = json.load(f)
    try:
        records = data['Data']['Dataset']
    except (KeyError, TypeError):
        raise ValueError('JSON needs Data.Dataset list') from None
    if not isinstance(records, list):
        raise ValueError('JSON Data.Dataset must be a list')
    groups = defaultdict(list)
    ids = set()
    for i, record in enumerate(records, 1):
        if not isinstance(record, dict) or not REQUIRED_JSON.issubset(record):
            raise ValueError(f'JSON record {i} missing required fields')
        if not record['DataID']:
            raise ValueError(f'JSON record {i} has missing DataID')
        ids.add(str(record['DataID']))
        bmi = numeric(record['BMI'], 'BMI', i)
        glucose = numeric(record['Glucose'], 'Glucose', i)
        groups[bmi_group(bmi)].append(glucose)
    if not groups:
        raise ValueError('JSON contains no observations')
    return summarize(groups), {'rows':len(records), 'distinct_data_ids':len(ids)}


def read_xml(path):
    root = ET.parse(path).getroot()
    groups = defaultdict(list)
    ids = set()
    for i, node in enumerate(root.findall('.//dataset'), 1):
        row = {child.tag: child.text for child in node}
        if not REQUIRED_XML.issubset(row):
            raise ValueError(f'XML dataset {i} missing required fields')
        if not row['DataID'] or not row['Location']:
            raise ValueError(f'XML dataset {i} missing DataID or Location')
        ids.add(row['DataID'])
        before = numeric(row['BP_Before'], 'BP_Before', i)
        after = numeric(row['BP_After'], 'BP_After', i)
        groups[row['Location'].strip()].append(before - after)
    if not groups:
        raise ValueError('XML contains no dataset elements')
    return summarize(groups), {'rows':sum(map(len, groups.values())), 'distinct_data_ids':len(ids)}


def write_csv(path, values):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['group','n','mean'])
        writer.writeheader()
        writer.writerows(values)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, default=ROOT/'data'/'csv_final_1.csv')
    parser.add_argument('--json', type=Path, default=ROOT/'data'/'json_final_1.json')
    parser.add_argument('--xml', type=Path, default=ROOT/'data'/'xml_final_2.xml')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'outputs')
    args = parser.parse_args(argv)
    results = {}
    for key, filename, loader in [('csv', args.csv, read_csv), ('json', args.json, read_json), ('xml', args.xml, read_xml)]:
        summaries, metrics = loader(filename)
        results[key] = {'source':filename.name, 'metrics':metrics, 'groups':summaries}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir/'glucose_by_csv_group.csv', results['csv']['groups'])
    write_csv(args.output_dir/'glucose_by_bmi_group.csv', results['json']['groups'])
    write_csv(args.output_dir/'bp_difference_by_location.csv', results['xml']['groups'])
    (args.output_dir/'summary.json').write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({k: v['metrics'] for k,v in results.items()}, indent=2))
    print('Wrote 4 analytical outputs to', args.output_dir)


if __name__ == '__main__':
    main()
