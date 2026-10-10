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

    def test_recomputed_bool_sequence_must_be_refused(self):
        from chronicle import compute_hash
        c = Chronicle()
        c.append({"v": 0}, timestamp=1)
        item = c.append({"v": 1}, timestamp=2)
        item.index = True   # True == 1 in Python: must NOT pass.
        item.hash = compute_hash(item.index, item.timestamp, item.payload, item.prev_hash)
        self.assertFalse(c.verify()[0])

    def test_recomputed_float_sequence_must_be_refused(self):
        from chronicle import compute_hash
        c = Chronicle()
        c.append({"v": 0}, timestamp=1)
        item = c.append({"v": 1}, timestamp=2)
        item.index = 1.0
        item.hash = compute_hash(item.index, item.timestamp, item.payload, item.prev_hash)
        self.assertFalse(c.verify()[0])

    def test_recomputed_boolean_timestamp_must_be_refused(self):
        from chronicle import compute_hash
        c = Chronicle()
        item = c.append({"v": 0}, timestamp=1)
        item.timestamp = True
        item.hash = compute_hash(item.index, item.timestamp, item.payload, item.prev_hash)
        self.assertFalse(c.verify()[0])

    def test_malformed_entry_must_fail_closed_without_exception(self):
        c = Chronicle()
        c.append({"v": 0}, timestamp=1)
        c.entries.append(object())
        self.assertFalse(c.verify()[0])

    def test_corrupted_disk_history_must_refuse_construction(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "history.jsonl"
            c = Chronicle(str(path))
            c.append({"value": 1}, timestamp=1)
            c.append({"value": 2}, timestamp=2)
            lines = path.read_text(encoding="utf-8").splitlines()
            first = json.loads(lines[0])
            first["payload"]["value"] = 999
            lines[0] = json.dumps(first)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                Chronicle(str(path))

    def test_rehashed_broken_link_must_refuse_construction(self):
        from chronicle import compute_hash
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "history.jsonl"
            c = Chronicle(str(path))
            c.append({"value": 1}, timestamp=1)
            c.append({"value": 2}, timestamp=2)
            lines = path.read_text(encoding="utf-8").splitlines()
            second = json.loads(lines[1])
            second["prev_hash"] = "f" * 64
            second["hash"] = compute_hash(
                second["index"], second["timestamp"],
                second["payload"], second["prev_hash"])
            lines[1] = json.dumps(second)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                Chronicle(str(path))

    def test_rehashed_bool_index_on_disk_must_refuse_construction(self):
        from chronicle import compute_hash
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "history.jsonl"
            c = Chronicle(str(path))
            c.append({"value": 1}, timestamp=1)
            c.append({"value": 2}, timestamp=2)
            lines = path.read_text(encoding="utf-8").splitlines()
            second = json.loads(lines[1])
            second["index"] = True
            second["hash"] = compute_hash(
                second["index"], second["timestamp"],
                second["payload"], second["prev_hash"])
            lines[1] = json.dumps(second)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                Chronicle(str(path))

    def test_healthy_disk_history_still_resumes(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "history.jsonl"
            c = Chronicle(str(path))
            c.append({"value": 1}, timestamp=1)
            c.append({"value": 2}, timestamp=2)
            resumed = Chronicle(str(path))
            self.assertEqual(resumed.head(), c.head())
            self.assertTrue(resumed.verify()[0])

    def test_valid_anchor_still_works(self):
        c = Chronicle(); c.append({'v': 0}, timestamp=1)
        self.assertTrue(verify_against_anchor(c, make_anchor(c))[0])


if __name__ == '__main__':
    unittest.main()
