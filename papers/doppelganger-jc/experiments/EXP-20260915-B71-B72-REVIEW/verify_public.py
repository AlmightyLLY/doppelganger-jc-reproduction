"""Verify public file hashes, then recompute scores and recorded-token checks."""
import hashlib,json
from pathlib import Path
from audit_public import audit as audit_scores
from audit_tokens import audit as audit_tokens
P=Path(__file__).resolve().parent
def main():
 manifest=json.loads((P/'MANIFEST.json').read_text())
 for r in manifest['files']:
  p=P/r['path'];b=p.read_bytes()
  assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],r['path']
 result={'status':'PASS','hashes_checked':len(manifest['files']),'scores':audit_scores(),'recorded_tokens':audit_tokens(),'scope':'Offline evidence consistency; not model rerun, independent human validation or mechanism verification'}
 print(json.dumps(result,indent=2));return result
if __name__=='__main__':main()
