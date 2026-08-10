#!/usr/bin/env python3
"""Persist one deterministic runtime-local ST1-042 family selection."""
from __future__ import annotations
import argparse,json,os
from pathlib import Path

def runtime(name:str)->Path: return Path(os.environ['LOCALAPPDATA'])/'EnterpriseAI'/'runtime'/name
p=argparse.ArgumentParser(); p.add_argument('--input',type=Path,default=runtime('st1-042-linkage-discovery.json')); p.add_argument('--alias',required=True); p.add_argument('--output',type=Path,default=runtime('st1-042-selection-manifest.json')); a=p.parse_args()
d=json.loads(a.input.read_text(encoding='utf-8')); f=next((x for x in d['top_families'] if x['alias']==a.alias),None)
if not f: raise SystemExit('selected alias is not in linkage output')
a.output.write_text(json.dumps({'alias':f['alias'],'relative_locator':f['relative_locator'],'selection_signature':{'document_count':f['document_count'],'probeable_document_count':f['probeable_document_count'],'extension_distribution':f['extension_distribution'],'aggregate_size_bytes':f['aggregate_size_bytes'],'linkage_signals':f['lead_signals']},'files':f['files']},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'alias':f['alias'],'document_count':f['document_count'],'probeable_document_count':f['probeable_document_count'],'aggregate_size_bytes':f['aggregate_size_bytes'],'runtime_local_only':True},separators=(',',':')))
