#!/usr/bin/env python3
"""Read targeted sheet cells from the bounded ST1-046 TWRP workbook locally."""
from __future__ import annotations
import argparse,json,os,zipfile
from datetime import UTC,datetime
from pathlib import Path
from xml.etree import ElementTree

TARGET_ALIAS="source-a08f4a79cf2116b1"
TARGET_SHEET_INDEXES={1,3,4,5,6,7,9,10,17,23,25,26}
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
REL='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
PKG='{http://schemas.openxmlformats.org/package/2006/relationships}'
def runtime(n:str)->Path:return Path(os.environ['LOCALAPPDATA'])/'EnterpriseAI'/'runtime'/n
def shared_strings(z:zipfile.ZipFile)->list[str]:
 if 'xl/sharedStrings.xml' not in z.namelist():return []
 root=ElementTree.fromstring(z.read('xl/sharedStrings.xml'))
 return [''.join(si.itertext()) for si in root.findall(f'{NS}si')]
def main()->int:
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--input',type=Path,default=runtime('st1-046-mrp-structure.json'));p.add_argument('--output',type=Path,default=runtime('st1-046-twrp-cells.json'));a=p.parse_args()
 d=json.loads(a.input.read_text(encoding='utf-8'));item=next((x for x in d['documents'] if x['source_alias']==TARGET_ALIAS),None)
 if not item:raise SystemExit('TWRP source alias unavailable')
 source=a.root/item['relative_locator']
 if not source.is_file() or source.stat().st_size!=item['indexed_size_bytes']:raise SystemExit('TWRP source revalidation failed')
 with zipfile.ZipFile(source) as z:
  ss=shared_strings(z); wb=ElementTree.fromstring(z.read('xl/workbook.xml'));rels=ElementTree.fromstring(z.read('xl/_rels/workbook.xml.rels'))
  relmap={r.attrib['Id']:r.attrib['Target'].lstrip('/') for r in rels.findall(f'{PKG}Relationship')}
  sheets=[]
  for index,s in enumerate(wb.findall(f'.//{NS}sheet'),start=1):
   if index not in TARGET_SHEET_INDEXES:continue
   rid=s.attrib.get(f'{REL}id');target=relmap[rid]
   if not target.startswith('xl/'):target='xl/'+target
   root=ElementTree.fromstring(z.read(target));cells=[]
   for cell in root.findall(f'.//{NS}c'):
    ref=cell.attrib.get('r');ctype=cell.attrib.get('t');v=cell.find(f'{NS}v');formula=cell.find(f'{NS}f')
    value=None if v is None else v.text
    if ctype=='s' and value is not None:
     value=ss[int(value)] if int(value)<len(ss) else None
    elif ctype=='inlineStr':
     node=cell.find(f'.//{NS}t');value=None if node is None else node.text
    if value not in (None,'') or formula is not None:
     cells.append({'cell':ref,'value':value,'formula':None if formula is None else formula.text,'literal_vs_formula':'formula' if formula is not None else 'literal'})
   sheets.append({'sheet_index':index,'sheet_name':s.attrib.get('name'), 'cell_count':len(cells),'cells':cells})
 out={'schema_version':'st1-046-twrp-cells-v1','generated_utc':datetime.now(UTC).isoformat(),'source_alias':TARGET_ALIAS,'selected_sheet_indexes':sorted(TARGET_SHEET_INDEXES),'sheets':sheets,'boundaries':{'read_only':True,'cell_provenance_preserved':True,'external_model_use':False,'platform_persistence':False,'raw_output_outside_git':True}}
 a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'source_alias':TARGET_ALIAS,'sheets_extracted':len(sheets),'cell_count':sum(x['cell_count'] for x in sheets),'output_outside_git':True},separators=(',',':')))
 return 0
if __name__=='__main__':raise SystemExit(main())
