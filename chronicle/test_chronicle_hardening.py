"""Fail-before/fix-after regression checks for the current Cathedral Chronicle.

Run: PYTHONPATH=chronicle python -m unittest discover -s tests -p 'test_chronicle_hardening.py' -v
"""
import json
import math
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from chronicle import Chronicle, make_anchor, verify_against_anchor


class ChronicleHardeningTests(unittest.TestCase):
    def test_refuse_append_after_existing_entry_tampered(self):
        c = Chronicle()
        c.append({"ok": 1}, timestamp=1)
        c.entries[0].payload["ok"] = 2
        before = len(c.entries)
        with self.assertRaises(ValueError):
            c.append({"new": 2}, timestamp=2)
        self.assertEqual(len(c.entries), before)

    def test_reject_disk_drift_after_open(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'log.jsonl'
            c = Chronicle(str(p))
            c.append({"value": 1}, timestamp=1)
            p.write_text('', encoding='utf-8')
            with self.assertRaises(ValueError):
                c.append({"value": 2}, timestamp=2)
            self.assertEqual(len(c.entries), 1)

    def test_failure_before_write_does_not_change_memory(self):
        with tempfile.TemporaryDirectory() as d:
            c = Chronicle(str(Path(d) / 'missing' / 'log.jsonl'))
            with self.assertRaises(OSError):
                c.append({"new": 1}, timestamp=1)
            self.assertEqual(len(c.entries), 0)

    def test_failed_fsync_poisoned_and_never_retried_silently(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'log.jsonl'
            c = Chronicle(str(p))
            with patch('os.fsync', side_effect=OSError('simulated unknown durability')):
                with self.assertRaises(OSError):
                    c.append({"first": 1}, timestamp=1)
            self.assertEqual(len(c.entries), 0)
            with self.assertRaises(RuntimeError):
                c.append({"second": 2}, timestamp=2)
            self.assertEqual(len(Chronicle(str(p)).entries), 1)

    def test_no_caller_owned_payload_alias(self):
        c = Chronicle()
        obj = {"k": [1]}
        c.append(obj, timestamp=1)
        obj['k'].append(2)
        self.assertEqual(c.entries[0].payload, {"k": [1]})
        self.assertTrue(c.verify()[0])

    def test_refuse_nonfinite_timestamp_and_payload(self):
        c = Chronicle()
        for invalid in [float('nan'), float('inf'), -float('inf'), True]:
            with self.subTest(timestamp=str(invalid)):
                with self.assertRaises((ValueError, TypeError)):
                    c.append({'k': 'v'}, timestamp=invalid)
        for invalid in [float('nan'), float('inf')]:
            with self.subTest(payload=str(invalid)):
                with self.assertRaises((ValueError, TypeError)):
                    c.append({'k': invalid}, timestamp=1)
        self.assertEqual(len(c.entries), 0)

    def test_refuse_duplicate_keys_on_reload(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'log.jsonl'
            c = Chronicle(str(p)); c.append({'v': 0}, timestamp=1)
            p.write_text(p.read_text().replace('"index": 0', '"index": 0, "index": 0'), encoding='utf-8')
            with self.assertRaises(ValueError):
                Chronicle(str(p))

    def test_refuse_nan_on_reload(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'log.jsonl'
            c = Chronicle(str(p)); c.append({'v': 0}, timestamp=1)
            p.write_text(p.read_text().replace('"timestamp": 1', '"timestamp": NaN'), encoding='utf-8')
            with self.assertRaises(ValueError):
                Chronicle(str(p))

    def test_malformed_anchor_refuses_not_exception(self):
        c = Chronicle(); c.append({'v': 0}, timestamp=1)
        for invalid in [None, {}, {'count': True, 'head': c.head(), 'merkle_root': c.merkle_root()},
                        {'count': 1, 'head': 'bad', 'merkle_root': c.merkle_root()},
                        {**make_anchor(c), 'authority': 'GRANTED'}]:
            with self.subTest(invalid=invalid):
                ok, _ = verify_against_anchor(c, invalid)
                self.assertFalse(ok)

    def test_valid_anchor_still_works(self):
        c = Chronicle(); c.append({'v': 0}, timestamp=1)
        self.assertTrue(verify_against_anchor(c, make_anchor(c))[0])


if __name__ == '__main__':
    unittest.main()
