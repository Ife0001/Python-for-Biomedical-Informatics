"""Create fictional clinical measurement records for reproducible demonstrations."""
from pathlib import Path
import csv
import random

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['record_id','group','bmi','glucose_mg_dl','systolic_before','systolic_after','diastolic_before','diastolic_after']


def generate(destination=ROOT / 'data' / 'synthetic_measurements.csv', n=120):
    rng = random.Random(2026)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for i in range(n):
        bmi = round(rng.uniform(19, 39), 1)
        glucose = round(rng.uniform(75, 185), 1)
        sbp = rng.randint(112, 170)
        dbp = rng.randint(68, 105)
        records.append({'record_id':f'REC-{i+1:04}', 'group':['A','B','C'][i%3],
                        'bmi':bmi, 'glucose_mg_dl':glucose,
                        'systolic_before':sbp, 'systolic_after':sbp-rng.randint(-4,15),
                        'diastolic_before':dbp, 'diastolic_after':dbp-rng.randint(-4,9)})
    # Deliberate data issues for quality-assurance exercises.
    records[2]['glucose_mg_dl'] = ''
    records[8]['bmi'] = 'unknown'
    records[13]['bmi'] = 0
    records[21]['systolic_after'] = ''
    records[34]['glucose_mg_dl'] = 999
    records.append(records[5].copy())  # Exact duplicate, same record identifier.
    with destination.open('w', newline='', encoding='utf-8') as handle:
        writer=csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    print(f'Generated {len(records)} fictional rows ({n} unique record IDs) in {destination}')

if __name__ == '__main__':
    generate()
