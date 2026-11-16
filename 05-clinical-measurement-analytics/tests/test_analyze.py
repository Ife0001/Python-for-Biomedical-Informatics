import unittest
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyze import analyze_frame

COLUMNS = ['record_id','group','bmi','glucose_mg_dl','systolic_before','systolic_after','diastolic_before','diastolic_after']

def row(rid='x', bmi='25', glucose='110'):
    return dict(zip(COLUMNS,[rid,'A',bmi,glucose,'140','130','90','84']))

class MeasurementTests(unittest.TestCase):
    def test_deduplicate_exact_rows(self):
        group,_,_,q=analyze_frame(pd.DataFrame([row(),row()]))
        self.assertEqual(q['exact_duplicate_rows_removed'],1)
        self.assertEqual(group['records'].iloc[0],1)
    def test_conflicting_id_rejected(self):
        with self.assertRaisesRegex(ValueError,'conflicting duplicate'):
            analyze_frame(pd.DataFrame([row(),row(glucose='120')]))
    def test_missing_and_out_of_range(self):
        _,_,missing,q=analyze_frame(pd.DataFrame([row(bmi='0',glucose=''),row('y',bmi='22',glucose='999')]))
        self.assertEqual(q['out_of_range_values_masked']['bmi'],1)
        self.assertEqual(q['out_of_range_values_masked']['glucose_mg_dl'],1)
        self.assertEqual(int(missing.set_index('field').loc['glucose_mg_dl','missing_or_invalid']),2)
    def test_group_bp_difference(self):
        g,_,_,_=analyze_frame(pd.DataFrame([row()]))
        self.assertEqual(float(g['mean_systolic_change'].iloc[0]),-10)
    def test_bmi_cutoff(self):
        _,b,_,_=analyze_frame(pd.DataFrame([row('a','24.9'),row('b','25'),row('c','30')]))
        counts=dict(zip(b['bmi_category'].astype(str),b['records']))
        self.assertEqual((counts['Normal'],counts['Overweight'],counts['Obesity']),(1,1,1))
    def test_schema(self):
        with self.assertRaisesRegex(ValueError,'Missing required'):
            analyze_frame(pd.DataFrame({'record_id':['a']}))

if __name__=='__main__':unittest.main()
