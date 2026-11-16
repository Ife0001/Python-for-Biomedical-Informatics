import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyze import bmi_group,read_csv,read_json,read_xml,numeric

class FormatTests(unittest.TestCase):
    def test_bmi_boundaries(self):
        self.assertEqual([bmi_group(v) for v in [18.49,18.5,24.9,25,29.99,30]], ['Under 18.5','18.5–24.9','18.5–24.9','25.0–29.9','25.0–29.9','30.0 or higher'])
    def test_invalid_numeric(self):
        with self.assertRaises(ValueError): numeric('NaN','Glucose',2)
    def test_csv_schema(self):
        with TemporaryDirectory() as d:
            p=Path(d)/'bad.csv';p.write_text('DataID,Glucose\n1,12\n')
            with self.assertRaisesRegex(ValueError,'missing required columns'):read_csv(p)
    def test_mixed_formats(self):
        from subprocess import run
        root=Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as d:
            # A test-only copy of the fictional source generator, not private data
            from importlib.util import spec_from_file_location,module_from_spec
            # Verify actual I/O with small temporary data sets
            p=Path(d)
            (p/'in.csv').write_text('DataID,Glucose,Location,Group\nx,100,A,1\ny,120,B,1\n')
            (p/'in.json').write_text('{"Data":{"Dataset":[{"DataID":"z","BMI":"25","Glucose":"130"}]}}')
            (p/'in.xml').write_text('<data><dataset><DataID>a</DataID><BP_Before>145</BP_Before><BP_After>125</BP_After><Location>A</Location></dataset></data>')
            self.assertEqual(read_csv(p/'in.csv')[0][0]['mean'],110)
            self.assertEqual(read_json(p/'in.json')[0][0]['group'],'25.0–29.9')
            self.assertEqual(read_xml(p/'in.xml')[0][0]['mean'],20)

if __name__=='__main__':unittest.main()
