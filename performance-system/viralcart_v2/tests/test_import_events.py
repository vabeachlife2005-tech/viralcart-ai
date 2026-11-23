import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import import_events
class ImportTests(unittest.TestCase):
 def test_dry_run_and_dedup(self):
  event={'event_id':'lead-1','occurred_at':'2026-11-23T11:00:00+00:00','kind':'lead','source':'site','evidence':'https://example.com','status':'verified'}
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'events.jsonl';p.write_text(json.dumps(event)+'\n')
   with patch.object(import_events.viralcart,'read_events',return_value=[]):
    self.assertEqual(import_events.import_file(p,True)['accepted'],1)
   with patch.object(import_events.viralcart,'read_events',return_value=[event]):
    self.assertEqual(import_events.import_file(p,True)['duplicates_skipped'],1)
 def test_rejects_unapproved_send(self):
  event={'event_id':'send-1','occurred_at':'2026-11-23T11:00:00+00:00','kind':'email_sent','source':'gmail','evidence':'gmail-id','status':'verified'}
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'events.jsonl';p.write_text(json.dumps(event)+'\n')
   with patch.object(import_events.viralcart,'read_events',return_value=[]):
    with self.assertRaises(ValueError):import_events.import_file(p,True)
if __name__=='__main__':unittest.main()
