import unittest,tempfile,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from audit_replay import audit,load,reconcile_damage
from ensemble import wilson
class ReplayTests(unittest.TestCase):
    def fixture(self):
        return [{'kind':'world_manifest','seed':17911097197626437575,'rng_seed':1},
        {'kind':'milestone','event':'dragon_damage','time_years':1,'value_a':4,'value_b':196},
        {'kind':'resource_event','event':'golem_damaged_dragon','time_years':10,'value':4,'remaining':196},
        {'kind':'counter_keyframe','time_years':11,'dragon_health':200}]
    def test_exact_seed(self):self.assertEqual(audit(self.fixture())['seed_u64'],'17911097197626437575')
    def test_cross_record_conflicts(self):self.assertEqual({x['code'] for x in audit(self.fixture())['findings']},{'damage_clock_mismatch','counter_health_regression'})
    def test_reconcile_preserves_original(self):
        original=self.fixture();fixed=reconcile_damage(original)
        self.assertEqual(original[1]['time_years'],1);self.assertEqual(fixed[1]['time_years'],10);self.assertEqual(fixed[1]['audit_original_time_years'],1)
    def test_refuse_ambiguous_repair(self):
        rows=self.fixture();rows[2]['value']=5
        with self.assertRaises(ValueError):reconcile_damage(rows)
    def test_health_conservation(self):
        rows=self.fixture();rows[1]['value_b']=190
        self.assertIn('health_transition_inconsistent',[x['code'] for x in audit(rows)['findings']])
    def test_zero_preserved(self):
        rows=self.fixture()[:1]+[{'kind':'milestone','event':'dragon_damage','time_years':1,'value_a':205,'value_b':0}]
        self.assertEqual(audit(rows)['last_damage_health'],0)
    def test_malformed_and_nonfinite_rejected(self):
        for text in ('{"kind":"world_manifest"}\nBAD','{"kind":"world_manifest"}\n{"kind":"x","time_years":NaN}','{"kind":"world_manifest"}\n{"kind":"x","time_years":-1}'):
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/'input.jsonl';p.write_text(text)
                with self.assertRaises(ValueError):load(p)
    def test_terminal_invariant(self):
        rows=self.fixture()[:1]+[{'kind':'run_summary','time_years':1,'completed':False,'golem_accounting_delta':1,'skeleton_accounting_delta':0,'creeper_accounting_delta':0}]
        self.assertIn('resource_accounting_nonzero',[x['code'] for x in audit(rows)['findings']])
    def test_wilson_no_false_certainty(self):
        self.assertGreater(wilson(0,2)[1],0);self.assertLess(wilson(2,2)[0],1);self.assertIsNone(wilson(0,0))
if __name__=='__main__':unittest.main()
