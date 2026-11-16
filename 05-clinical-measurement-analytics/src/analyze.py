"""Validate fictional clinical measurements and output aggregate-only analytics.

Rule thresholds below are illustrative technical quality checks, not clinical decision rules.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ['record_id','group','bmi','glucose_mg_dl','systolic_before','systolic_after','diastolic_before','diastolic_after']
NUMERIC = REQUIRED[2:]
PLAUSIBLE = {'bmi':(10,80),'glucose_mg_dl':(30,600), 'systolic_before':(60,250),
             'systolic_after':(60,250), 'diastolic_before':(30,160),'diastolic_after':(30,160)}


def analyze_frame(raw):
    missing = [c for c in REQUIRED if c not in raw.columns]
    if missing:
        raise ValueError('Missing required columns: ' + ', '.join(missing))
    df = raw[REQUIRED].copy()
    source_rows = len(df)
    df['record_id'] = df['record_id'].astype('string').str.strip()
    df['group'] = df['group'].astype('string').str.strip()
    df = df.drop_duplicates()
    exact_duplicates_removed = source_rows - len(df)
    invalid_id = df['record_id'].isna() | df['record_id'].eq('')
    missing_ids = int(invalid_id.sum())
    df = df.loc[~invalid_id].copy()
    repeated_ids = int(df['record_id'].duplicated().sum())
    if repeated_ids:
        raise ValueError(f'{repeated_ids} conflicting duplicate record IDs; manual review required')
    invalid_counts = {}
    for col in NUMERIC:
        parsed = pd.to_numeric(df[col], errors='coerce')
        low, high = PLAUSIBLE[col]
        outside = parsed.notna() & ~parsed.between(low, high)
        invalid_counts[col] = int(outside.sum())
        df[col] = parsed.mask(outside)
    df['group'] = df['group'].replace('', pd.NA).fillna('Unknown')
    bmi = df['bmi']
    df['bmi_category'] = pd.cut(bmi, bins=[10,18.5,25,30,80],
                               labels=['Underweight','Normal','Overweight','Obesity'],
                               right=False, include_lowest=True)
    df['systolic_change'] = df['systolic_after'] - df['systolic_before']
    df['diastolic_change'] = df['diastolic_after'] - df['diastolic_before']
    # All summaries are aggregate-only: no record IDs are exported.
    group = df.groupby('group', dropna=False).agg(
        records=('record_id','size'),
        glucose_observed=('glucose_mg_dl','count'),
        glucose_mean=('glucose_mg_dl','mean'),
        bmi_observed=('bmi','count'),
        bmi_mean=('bmi','mean'),
        systolic_pairs=('systolic_change','count'),
        mean_systolic_change=('systolic_change','mean'),
        mean_diastolic_change=('diastolic_change','mean')).reset_index()
    bmi_group = df.groupby('bmi_category', observed=False).agg(
        records=('record_id','count'), glucose_observed=('glucose_mg_dl','count'),
        glucose_mean=('glucose_mg_dl','mean')).reset_index()
    missingness = pd.DataFrame([{'field':col, 'missing_or_invalid':int(df[col].isna().sum()),
                                 'percent_missing_or_invalid':round(100*df[col].isna().mean(),2) if len(df) else 0}
                                for col in NUMERIC])
    quality = {'source_rows':source_rows, 'exact_duplicate_rows_removed':exact_duplicates_removed,
               'rows_missing_record_id_removed':missing_ids,'distinct_records_analyzed':len(df),
               'out_of_range_values_masked':invalid_counts,
               'measurement_range_rules':'illustrative data checks; not clinical standards',
               'source':'synthetic demonstration data'}
    return group, bmi_group, missingness, quality


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, default=ROOT/'data'/'synthetic_measurements.csv')
    p.add_argument('--output-dir', type=Path, default=ROOT/'outputs')
    args=p.parse_args()
    if not args.input.is_file():
        p.error(f'Input missing: {args.input}. Run python src/generate_demo.py first.')
    raw=pd.read_csv(args.input, dtype='string', keep_default_na=True)
    by_group, by_bmi, missingness, quality=analyze_frame(raw)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    by_group.to_csv(args.output_dir/'measurements_by_group.csv',index=False,float_format='%.2f')
    by_bmi.to_csv(args.output_dir/'glucose_by_bmi_category.csv',index=False,float_format='%.2f')
    missingness.to_csv(args.output_dir/'measurement_missingness.csv',index=False)
    (args.output_dir/'quality_report.json').write_text(json.dumps(quality,indent=2),encoding='utf-8')
    print(json.dumps(quality,indent=2))
    print('Saved four aggregate reports to',args.output_dir)

if __name__=='__main__':
    main()
