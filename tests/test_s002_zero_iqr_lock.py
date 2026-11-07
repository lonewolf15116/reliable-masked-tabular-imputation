"""S002 regression lock test; run after committing generated training stats.

.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_s002_*.py" -v
Requires local raw Adult source and S001 manifest. Does not fit a model.
"""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"artifacts/stats/adult_train_feature_stats.json"
SCRIPT=ROOT/"scripts/s002_adult_train_stats.py"

class TestS002ZeroIqrLock(unittest.TestCase):
    def test_locked_stats_and_exact_zero_iqr_set(self):
        self.assertTrue(TARGET.is_file(),"S002 stats not yet generated/committed")
        spec=importlib.util.spec_from_file_location("s002_audit",SCRIPT)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        import os
        previous=Path.cwd()
        try:
            os.chdir(ROOT)
            generated,computed=module.construct()
        finally:
            os.chdir(previous)
        self.assertEqual(TARGET.read_bytes(),generated,
                         "Any change to S001 indices, source, numeric IQRs, vocab, or the locked set is a regression")
        locked=json.loads(TARGET.read_text(encoding="utf-8"))
        recorded=locked["exact_zero_iqr_numeric_features"]
        recalculated=sorted(k for k,v in computed["numeric_feature_stats"].items()
                            if v["iqr"]==0.0)
        self.assertEqual(recorded,recalculated,"The exact-zero-IQR feature set changed")
        self.assertEqual(locked["primary_normalized_error_excludes"],recorded)
        self.assertNotIn("income",locked["imputation_feature_names"])

if __name__=="__main__":
    unittest.main()
