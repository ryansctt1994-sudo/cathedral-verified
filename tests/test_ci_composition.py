"""Pin the reconciled Cathedral CI surface.

These checks read the checked-in workflow and Makefile. They do not simulate
RTL and do not establish silicon, witness, or production evidence.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CI = ROOT / ".github" / "workflows" / "ci.yml"
MAKEFILE = ROOT / "Makefile"


class ReconciledCiTests(unittest.TestCase):
    def test_workflow_keeps_chronicle_and_rtl_jobs(self):
        text = CI.read_text(encoding="utf-8")
        self.assertIn("\n  chronicle:\n", text)
        self.assertIn("\n  rtl-simulation:\n", text)
        self.assertIn("python3 test_chronicle.py", text)
        self.assertIn("python3 -m unittest -v test_chronicle_hardening", text)
        self.assertIn("make test-hw", text)
        self.assertIn("hardware/lucifer_latch/test_negative_control.py", text)

    def test_local_make_runs_chronicle_hardening(self):
        text = MAKEFILE.read_text(encoding="utf-8")
        self.assertIn("test-chronicle-hardening", text)
        self.assertIn("test_chronicle_hardening", text)
        self.assertIn("test-hw", text)


if __name__ == "__main__":
    unittest.main()
