import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from cathedral_forge_final import CathedralForge, SimulatedLatchHardware
from recognition_kernel import (
    LANGUAGE_ID,
    MAX_INPUT_BYTES,
    RecognitionError,
    canonical_serialize,
    execute_recognized_governance_request,
    parse_governance_request,
)


class RecognitionKernelTests(unittest.TestCase):
    def assert_rejected(self, raw, code):
        with self.assertRaises(RecognitionError) as caught:
            parse_governance_request(raw)
        self.assertEqual(caught.exception.code, code)

    def test_valid_request_is_typed_canonical_and_receipted(self):
        raw = '{"prompt":"Review this evidence.","strand":"lead"}'
        recognized = parse_governance_request(raw)

        self.assertEqual(recognized.request.prompt, "Review this evidence.")
        self.assertEqual(recognized.receipt.language_id, LANGUAGE_ID)
        self.assertEqual(recognized.receipt.parser_evidence_level, "P3")
        self.assertFalse(recognized.receipt.side_effects_during_parse)
        self.assertFalse(recognized.receipt.raw_input_retains_authority)
        self.assertEqual(canonical_serialize(recognized.request), recognized.canonical_bytes)
        self.assertEqual(len(recognized.receipt.canonical_sha256), 64)

    def test_duplicate_fields_are_rejected(self):
        self.assert_rejected('{"prompt":"one","prompt":"two"}', "duplicate_field")

    def test_truncated_input_is_rejected(self):
        self.assert_rejected('{"prompt":"unfinished"', "invalid_json")

    def test_trailing_garbage_and_valid_prefix_suffix_are_rejected(self):
        self.assert_rejected('{"prompt":"safe"} malicious_suffix', "invalid_json")

    def test_unknown_fields_are_rejected(self):
        self.assert_rejected('{"prompt":"safe","shell":"rm -rf /"}', "unknown_field")

    def test_mixed_prose_and_command_is_rejected(self):
        self.assert_rejected('Please execute: {"prompt":"safe"}', "invalid_json")

    def test_null_byte_injection_is_rejected(self):
        self.assert_rejected(b'{"prompt":"safe"}\x00', "null_byte")

    def test_invalid_encoding_is_rejected(self):
        self.assert_rejected(b"\xff\xfe{\x00}\x00", "null_byte")

    def test_unicode_normalization_variant_is_rejected(self):
        raw = json.dumps({"prompt": "Cafe\u0301"}, ensure_ascii=False)
        self.assert_rejected(raw, "non_canonical_unicode")

    def test_oversized_input_is_rejected(self):
        raw = b"{" + b" " * MAX_INPUT_BYTES + b"}"
        self.assert_rejected(raw, "input_too_large")

    def test_excessive_nesting_is_rejected_before_semantic_use(self):
        raw = '{"prompt":"safe","x":{"a":{"b":{"c":{"d":{"e":1}}}}}}'
        self.assert_rejected(raw, "excessive_nesting")

    def test_integer_overflow_and_boolean_confusion_are_rejected(self):
        self.assert_rejected('{"prompt":"safe","max_rounds":999999999999}', "out_of_range")
        self.assert_rejected('{"prompt":"safe","max_rounds":true}', "invalid_type")

    def test_non_finite_number_is_rejected(self):
        self.assert_rejected('{"prompt":"safe","max_rounds":1e999}', "non_finite_number")

    def test_reordered_fields_have_one_canonical_meaning(self):
        first = parse_governance_request(
            '{"prompt":"same","alpha_contribution":7,"omega_contribution":8}'
        )
        second = parse_governance_request(
            '{"omega_contribution":8,"prompt":"same","alpha_contribution":7}'
        )
        self.assertEqual(first.canonical_bytes, second.canonical_bytes)
        self.assertEqual(first.receipt.canonical_sha256, second.receipt.canonical_sha256)

    def test_defaults_and_explicit_defaults_are_endpoint_equivalent(self):
        implicit = parse_governance_request('{"prompt":"same"}')
        explicit = parse_governance_request(
            '{"prompt":"same","conversation_context":null,"strand":"lead",'
            '"require_conservation":true,"alpha_contribution":7,'
            '"omega_contribution":8,"max_rounds":2}'
        )
        self.assertEqual(implicit.canonical_bytes, explicit.canonical_bytes)

    def test_parse_failure_produces_no_partial_file_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assert_rejected('{"prompt":"safe"} trailing', "invalid_json")
            self.assertEqual(list(root.iterdir()), [])


class RecognitionIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_recognition_gate_precedes_forge_execution_and_state_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "chronicle.jsonl"
            forge = CathedralForge(
                hardware=SimulatedLatchHardware(authenticated=True),
                ledger_path=ledger_path,
            )
            raw = json.dumps(
                {
                    "prompt": "Review this bounded architecture proposal.",
                    "strand": "lead",
                    "require_conservation": True,
                    "alpha_contribution": 7,
                    "omega_contribution": 8,
                    "max_rounds": 2,
                },
                separators=(",", ":"),
            )

            response, receipt = await execute_recognized_governance_request(forge, raw)

            self.assertEqual(receipt.language_id, LANGUAGE_ID)
            self.assertTrue(ledger_path.exists())
            self.assertTrue(response.cathedral_state.intake_complete)
            self.assertTrue(response.cathedral_state.l5_chain_valid)

    async def test_invalid_raw_request_never_reaches_chronicle_or_hardware(self):
        class ExplodingHardware:
            def set_threat(self, level):
                raise AssertionError("hardware must not be touched")

            def trigger(self):
                raise AssertionError("hardware must not be touched")

            def read_status(self):
                raise AssertionError("hardware must not be touched")

        with tempfile.TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "chronicle.jsonl"
            forge = CathedralForge(hardware=ExplodingHardware(), ledger_path=ledger_path)

            with self.assertRaises(RecognitionError):
                await execute_recognized_governance_request(
                    forge,
                    '{"prompt":"safe","prompt":"smuggled"}',
                )

            self.assertFalse(ledger_path.exists())
            self.assertEqual(forge.ledger.entries, [])
            self.assertFalse(forge.cathedral.intake_complete)


if __name__ == "__main__":
    unittest.main()
