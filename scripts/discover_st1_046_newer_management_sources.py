#!/usr/bin/env python3
"""Find bounded metadata-only management-report candidates after a supplied cutoff.

This query uses only the completed runtime-local metadata index. Filename and
directory dates are discovery filters, not asserted reporting dates. Raw
locators and filenames stay in the runtime-local output.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,sqlite3,unicodedata
from collections import Counter,defaultdict
from datetime import UTC,datetime
from pathlib import Path

ALLOW={".pdf",".docx",".xlsx"}
TERMS={
 "management_status":("گزارش مدیریت","گزارش وضعیت","وضعیت پروژه","management report","status report","project status"),
 "periodic_progress":("گزارش پیشرفت","گزارش هفتگی","گزارش ماهانه","progress report","weekly report","monthly report"),
 "control_schedule":("کنترل پروژه","برنامه زمانبندی","برنامه زمان‌بندی","project control","time schedule","schedule","primavera","p6"),
}
NEGATIVE=("claim","legal","tender","bid","لایحه","دعاوی","حقوقی","مناقصه")
PERSIAN=str.maketrans("۰۱۲۳۴۵۶۷۸۹","0123456789")
DATE=re.compile(r"(?<!\d)(14\d{2})[._/\-\s]+(\d{1,2})(?!\d)")
def runtime(n:str)->Path: return Path(os.environ["LOCALAPPDATA"])/"EnterpriseAI"/"runtime"/n
def norm(s:str)->str:
 s=unicodedata.normalize("NFKC",s or "").translate(PERSIAN).replace("ي","ی").replace("ى","ی").replace("ك","ک")
 return " ".join(s.casefold().split())
def newer(s:str, cutoff:tuple[int,int])->bool:
 for y,m in DATE.findall(norm(s)):
  if (int(y),int(m))>cutoff: return True
 return False

p=argparse.ArgumentParser();p.add_argument("--database",type=Path,default=runtime("pilot_metadata_index.sqlite"));p.add_argument("--output",type=Path);p.add_argument("--task-id",default="st1-046");p.add_argument("--after-year",type=int,default=1402);p.add_argument("--after-month",type=int,default=6);p.add_argument("--limit",type=int,default=10);a=p.parse_args()
if a.after_month not in range(1,13): raise SystemExit("after-month must be 1..12")
if a.output is None: a.output=runtime(f"{a.task_id}-newer-management-discovery.json")
if not a.database.is_file(): raise SystemExit("runtime-local index unavailable")
cutoff=(a.after_year,a.after_month)
c=sqlite3.connect(a.database)
try: rows=c.execute("SELECT relative_locator,parent_relative_locator,source_alias,filename,extension,size_bytes,modified_utc FROM files WHERE enumeration_status='enumerated'").fetchall()
finally: c.close()
families=defaultdict(lambda:{"files":[],"signals":defaultdict(set),"dates":[],"negative":False})
for relative,parent,alias,name,ext,size,modified in rows:
 hay=f"{parent}/{name}"; probe=norm(hay)
 if not newer(hay,cutoff): continue
 item=families[parent]; item["files"].append({"relative_locator":relative,"source_alias":alias,"filename":name,"extension":ext,"size_bytes":int(size or 0),"modified_utc":modified})
 for category,terms in TERMS.items():
  for term in terms:
   if norm(term) in probe: item["signals"][category].add(term)
 item["negative"]|=any(norm(x) in probe for x in NEGATIVE)
 item["dates"].extend(DATE.findall(norm(hay)))
ranked=[]
for parent,item in families.items():
 files=item["files"]; allowed=[x for x in files if x["extension"].casefold() in ALLOW]; size=sum(x["size_bytes"] for x in files)
 if not allowed or item["negative"] or len(files)>80 or size>1_073_741_824: continue
 score=sum({"management_status":20,"periodic_progress":14,"control_schedule":9}[k]*min(3,len(v)) for k,v in item["signals"].items())+min(6,len(allowed)//2)
 if not item["signals"]: score+=1
 ranked.append({"alias":f"{a.task_id}-"+hashlib.sha256(parent.encode()).hexdigest()[:16],"relative_locator":parent,"score":score,"metadata_date_tokens":sorted(set(f"{y}/{int(m):02d}" for y,m in item["dates"])),"signals":{k:sorted(v) for k,v in item["signals"].items()},"file_count":len(files),"probeable_file_count":len(allowed),"extension_distribution":dict(sorted(Counter(x["extension"] for x in files).items())),"aggregate_size_bytes":size,"files":files})
ranked.sort(key=lambda x:(-x["score"],-x["probeable_file_count"],x["aggregate_size_bytes"],x["relative_locator"].casefold()))
out={"schema_version":f"{a.task_id}-newer-management-discovery-v1","generated_utc":datetime.now(UTC).isoformat(),"metadata_only":True,"threshold":f"filename_or_directory_date_token > {a.after_year}/{a.after_month:02d}","index_rows_queried":len(rows),"candidate_family_count":len(ranked),"candidates":ranked[:a.limit],"boundaries":{"content_opened":False,"new_smb_traversal":False,"external_model_use":False,"raw_output_outside_git":True}}
a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"metadata_only":True,"index_rows_queried":len(rows),"candidate_family_count":len(ranked),"reported_candidates":len(out["candidates"]),"output_outside_git":True},separators=(",",":")))
