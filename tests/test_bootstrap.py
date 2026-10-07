import tempfile
import unittest
from pathlib import Path

from bootstrap_policy import INV_BOOT_001, enforce_source_policy, inspect_file


class BootstrapPolicyTests(unittest.TestCase):
    def test_blob_breaks_noBlobs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "readable_source.py").write_text("print('auditable')\n", encoding="utf-8")
            (root / "opaque_payload.bin").write_bytes(b"\x7fELF\x00opaque")

            result = enforce_source_policy(root)

            self.assertFalse(result.accepted)
            self.assertEqual(result.state, "REJECT")
            self.assertTrue(any(v.rule == INV_BOOT_001 for v in result.violations))
            self.assertTrue(any(v.path == "opaque_payload.bin" for v in result.violations))

    def test_blobTool_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            tool = Path(tmp) / "vendor_tool"
            tool.write_bytes(b"MZ\x00precompiled-tool")

            violations = inspect_file(tool)

            self.assertTrue(violations)
            self.assertTrue(any(v.rule == INV_BOOT_001 for v in violations))

    def test_human_readable_source_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "module.py").write_text("VALUE = 717\n", encoding="utf-8")
            (root / "design.v").write_text("module design; endmodule\n", encoding="utf-8")
            (root / "README.md").write_text("Source-only fixture.\n", encoding="utf-8")

            result = enforce_source_policy(root)

            self.assertTrue(result.accepted)
            self.assertEqual(result.violations, ())

    def test_forbidden_extension_is_rejected_even_without_magic_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "payload.so"
            artifact.write_text("not actually executable", encoding="utf-8")

            violations = inspect_file(artifact)

            self.assertTrue(violations)
            self.assertIn("forbidden opaque or precompiled artifact type", violations[0].reason)


if __name__ == "__main__":
    unittest.main()
