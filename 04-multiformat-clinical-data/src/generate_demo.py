"""Generate small fictional, reproducible example files (never patient records)."""
import csv
import json
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
p = ROOT/'data'
p.mkdir(exist_ok=True)
with (p/'csv_final_1.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['DataID','Glucose','Location','Group'])
    w.writerows([['DEMO-C01','100','A','1'],['DEMO-C02','120','B','1'],['DEMO-C03','140','A','2']])
records=[{'DataID':'DEMO-J01','BMI':'18.4','Glucose':'90'}, {'DataID':'DEMO-J02','BMI':'24.9','Glucose':'110'}, {'DataID':'DEMO-J03','BMI':'25.0','Glucose':'120'}, {'DataID':'DEMO-J04','BMI':'30.0','Glucose':'140'}]
(p/'json_final_1.json').write_text(json.dumps({'Data': {'Dataset':records}},indent=2),encoding='utf-8')
r=ET.Element('data')
for row in [('DEMO-X01','140','120','A'),('DEMO-X02','130','125','A'),('DEMO-X03','150','135','B')]:
    d=ET.SubElement(r,'dataset')
    for tag,val in zip(['DataID','BP_Before','BP_After','Location'],row):ET.SubElement(d,tag).text=val
ET.ElementTree(r).write(p/'xml_final_2.xml',encoding='utf-8',xml_declaration=True)
print('Generated three fictional input files in data/')
