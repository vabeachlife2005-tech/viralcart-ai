import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from viralcart import validate,summarize,score
BASE={'event_id':'e1','occurred_at':'2026-11-23T11:00:00+00:00','kind':'lead','source':'official-site','evidence':'https://example.org/page','status':'verified'}
class TestScoreboard(unittest.TestCase):
 def test_valid(self):self.assertEqual(validate(BASE),BASE)
 def test_duplicate(self):
  with self.assertRaises(ValueError):validate(BASE,[BASE])
 def test_unapproved_send(self):
  with self.assertRaises(ValueError):validate({**BASE,'kind':'email_sent'})
 def test_no_denominator(self):self.assertIsNone(summarize([])['human_reply_rate'])
 def test_unverified_not_counted(self):self.assertEqual(summarize([{**BASE,'kind':'order_paid','amount_usd':75,'status':'estimated'}])['verified_revenue_usd'],0)
 def test_worker_rubric(self):
  e={**BASE,'kind':'worker_run','worker':'creative','deliverable':'sample','owner':'creative','next_action':'QA','rubric':{'evidence':30,'accuracy':25,'impact':20,'completion':15,'next_experiment':10}}
  self.assertEqual(score(e),100)
 def test_bad_rubric(self):
  e={**BASE,'kind':'worker_run','rubric':{'evidence':99}}
  with self.assertRaises(ValueError):score(e)
if __name__=='__main__':unittest.main()
