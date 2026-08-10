#!/usr/bin/env python3
"""Create local-only native acquisition metadata for one approved file."""
from __future__ import annotations
import hashlib,json,os
from datetime import UTC,datetime
from pathlib import Path

ROOT=Path(os.environ["EAI_ST1_061_ROOT"])
RT=Path(os.environ["LOCALAPPDATA"])/"EnterpriseAI"/"runtime"
disc=json.loads((RT/"st1-046-newer-management-discovery.json").read_text(encoding="utf-8"))
chosen=None
for family in disc["candidates"]:
 for item in family["files"]:
  if item["extension"].casefold() in {".pdf",".docx",".xlsx"}:
   source=ROOT/Path(item["relative_locator"])
   if source.is_file() and source.stat().st_size==int(item["size_bytes"]): chosen=(family,item,source);break
 if chosen: break
if not chosen: raise SystemExit("no approved bounded source available")
family,item,path=chosen; h=hashlib.sha256()
with path.open("rb") as f:
 for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
safe={"selection_alias":family["alias"],"source_alias":item["source_alias"],"extension":item["extension"],"size_bytes":path.stat().st_size,"original_fingerprint":h.hexdigest(),"acquisition_timestamp":datetime.now(UTC).isoformat(),"business_timestamp_state":"missing_not_inferred","authority_state":"not_verified","locator_fingerprint":hashlib.sha256(str(path.relative_to(ROOT)).encode()).hexdigest(),"source_reference":"runtime-local-only"}
(RT/"st1-061-native-acquisition.json").write_text(json.dumps(safe,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"acquired":True,"extension":safe["extension"],"size_bytes":safe["size_bytes"],"raw_locator_output":False},separators=(",",":")))
