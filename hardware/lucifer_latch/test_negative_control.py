#!/usr/bin/env python3
"""Negative control: a broken RTL threshold must produce failing simulator exit.

This checks our testbench's process-exit behavior, not silicon or timing closure.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
DUT = HERE / "lucifer_latch.v"
BENCH = HERE / "tb_lucifer_latch.v"
GOOD = "localparam THREAT_THRESHOLD    = 8'd191;"
BAD = "localparam THREAT_THRESHOLD    = 8'd255;"


def main() -> int:
    source = DUT.read_text(encoding="utf-8")
    if source.count(GOOD) != 1:
        print("REFUSED: expected single threshold constant not found", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="latch-negative-") as tmp:
        root = Path(tmp)
        bad_dut = root / "broken_lucifer_latch.v"
        bad_dut.write_text(source.replace(GOOD, BAD), encoding="utf-8")
        simulation = root / "sim_bad"
        compiled = subprocess.run(
            ["iverilog", "-g2012", "-o", str(simulation), str(bad_dut), str(BENCH)],
            cwd=root, capture_output=True, text=True, timeout=45, check=False,
        )
        if compiled.returncode:
            print("REFUSED: injected RTL did not compile; cannot test assertion gate")
            print(compiled.stdout + compiled.stderr, file=sys.stderr)
            return 2

        run = subprocess.run(
            ["vvp", str(simulation)], cwd=root, capture_output=True,
            text=True, timeout=60, check=False,
        )
        transcript = run.stdout + run.stderr
        if run.returncode == 0 or "VERDICT: DESIGN HAS FAILURES" not in transcript:
            print("FAIL: mutated RTL was not rejected by a failing assertion")
            print(f"vvp exit={run.returncode}\n{transcript}", file=sys.stderr)
            return 1

        if "FAIL:" not in transcript or "RTL_TESTBENCH_ASSERTION_FAILURE" not in transcript:
            print("FAIL: refusal did not prove a failed testbench assertion")
            print(transcript, file=sys.stderr)
            return 1

        print("MUTATION_THREAT_THRESHOLD_191_TO_255: REJECTED")
        print(f"vvp_exit: {run.returncode}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
