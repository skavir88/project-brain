#!/usr/bin/env python3
"""Revalidate and structurally inspect the bounded ST1-046 MRP-1402/12 family.

Only PDF/DOCX/XLSX members are opened locally. XLSX workbooks receive a
read-only OOXML structural pass first; raw content remains runtime-local.
"""
from __future__ import annotations
import argparse,json,os,sqlite3,zipfile
from datetime import UTC,datetime
from pathlib import Path
from xml.etree import ElementTree

ALLOW={".pdf",".docx",".xlsx"}
FAMILY_ALIASES={"st1-046-7297becd26ebbda6","st1-046-251e189ba1c0287c","st1-046-e17a52f281c1ecc4","st1-046-f1f91a08294160a9","st1-046-c6b4746986c7bfd3"}
def runtime(n:str)->Path: return Path(os.environ["LOCALAPPDATA"])/"EnterpriseAI"/"runtime"/n
def xlsx_structure(path:Path)->dict:
 with zipfile.ZipFile(path) as z:
  wb=ElementTree.fromstring(z.read('xl/workbook.xml'))
  sheets=[x.attrib.get('name','') for x in wb.findall('.//{*}sheet')]
  names=z.namelist()
  worksheet_parts=sorted(x for x in names if x.startswith('xl/worksheets/') and x.endswith('.xml'))
  return {'kind':'xlsx','sheet_names':sheets,'worksheet_part_count':len(worksheet_parts),'has_shared_strings':'xl/sharedStrings.xml' in names,'zip_member_count':len(names)}
def pdf_structure(path:Path)->dict:
 from pypdf import PdfReader
 r=PdfReader(str(path)); return {'kind':'pdf','page_count':len(r.pages),'direct_text_character_count':sum(len(p.extract_text() or '') for p in r.pages)}

p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--database',type=Path,default=runtime('pilot_metadata_index.sqlite'));p.add_argument('--discovery',type=Path,default=runtime('st1-046-newer-management-discovery.json'));p.add_argument('--output',type=Path,default=runtime('st1-046-mrp-structure.json'));a=p.parse_args()
if not a.root.is_dir() or not a.database.is_file() or not a.discovery.is_file(): raise SystemExit('required read-only source root or runtime state unavailable')
d=json.loads(a.discovery.read_text(encoding='utf-8')); relevant=[x for x in d['candidates'] if x['alias'] in FAMILY_ALIASES]
if len(relevant)!=5: raise SystemExit('MRP family discovery signature mismatch')
prefix=relevant[0]['relative_locator'].rsplit('/',1)[0]
c=sqlite3.connect(a.database)
try: rows=c.execute("SELECT relative_locator,source_alias,filename,extension,size_bytes,created_utc,modified_utc,metadata_fingerprint FROM files WHERE enumeration_status='enumerated' AND (parent_relative_locator=? OR parent_relative_locator LIKE ?) ORDER BY relative_locator",(prefix,prefix+'/%')).fetchall()
finally:c.close()
docs=[]
for relative,alias,name,ext,size,created,modified,fingerprint in rows:
 if ext.casefold() not in ALLOW: continue
 source=a.root/relative; item={'relative_locator':relative,'source_alias':alias,'filename':name,'extension':ext,'indexed_size_bytes':size,'indexed_created_utc':created,'indexed_modified_utc':modified,'metadata_fingerprint':fingerprint,'revalidation':{'available':source.is_file()}}
 if source.is_file():
  item['revalidation']['observed_size_bytes']=source.stat().st_size;item['revalidation']['size_matches']=source.stat().st_size==size
 if item['revalidation'].get('size_matches'):
  try:
   item['structure']=xlsx_structure(source) if ext.casefold()=='.xlsx' else pdf_structure(source);item['inspection_status']='inspected'
  except Exception as e:item['inspection_status']='error';item['error_type']=type(e).__name__
 else:item['inspection_status']='not_opened_revalidation_failed'
 docs.append(item)
out={'schema_version':'st1-046-mrp-structure-v1','generated_utc':datetime.now(UTC).isoformat(),'family_aliases':sorted(FAMILY_ALIASES),'selection_signature':{'family_file_count':len(rows),'allowlisted_file_count':len(docs),'excluded_file_count':len(rows)-len(docs)},'documents':docs,'boundaries':{'read_only':True,'xlsb_opened':False,'archives_opened':False,'vsdx_opened':False,'content_extraction_deferred_pending_structure':True,'external_model_use':False,'platform_persistence':False,'raw_output_outside_git':True}}
a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'family_file_count':len(rows),'allowlisted_file_count':len(docs),'available':sum(x['revalidation']['available'] for x in docs),'size_match':sum(x['revalidation'].get('size_matches') is True for x in docs),'inspected':sum(x['inspection_status']=='inspected' for x in docs),'errors':sum(x['inspection_status']=='error' for x in docs),'output_outside_git':True},separators=(',',':')))
