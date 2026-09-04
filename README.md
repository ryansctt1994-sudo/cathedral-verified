# cathedral-verified

Two narrow safety-oriented primitives with retained local test artifacts and reproducible test commands. Claims in this repository are intended to stay bounded to what the exact tests establish.

## Tested locally

### 1. Lucifer Latch — hardware veto RTL (`hardware/lucifer_latch/`)

An FPGA-oriented irreversible latch design (Verilog; Artix-7 / Arty A7-35T target). The retained Icarus Verilog simulation reports **8/8 checks passing**. Once the FSM reaches `TRIGGERED`, the tested software-controlled inputs do not return it to `ARMED`; `rst_n` resets it in the model.

The retained simulation reaches the veto at approximately **68,001 cycles ≈ 680.01 µs at an ideal 100 MHz simulation clock**. This result is **not currently classified as “on spec”** because the historical ~670 µs requirement is ambiguous: a maximum response deadline and a minimum deliberation floor are opposite requirements. See [hardware/lucifer_latch/TIMING_REQUIREMENT.md](hardware/lucifer_latch/TIMING_REQUIREMENT.md).

### 2. Chronicle — tamper-evident ledger (`chronicle/`)

A SHA-256 hash-chained append-only log. The retained local suite reports **15/15 adversarial checks passing** for the cases encoded in that suite. Field edits, re-hashing, reordering, deletion, forged inserts, and on-disk tampering are test targets. Head anchoring is the mechanism intended to address truncation/full-rewrite detection, but real protection requires the anchor to live outside the attacker's rewrite boundary.

## Reproduce

```bash
make test
# or individually:
make test-chronicle
make test-hw        # requires: iverilog
```

The current GitHub Actions workflow runs the Chronicle verification suite on pushes. Run the full command set in a fresh environment and retain raw logs before making a fresh reproduction claim for both primitives.

## Explicit nonclaims

- **The latch is tested in RTL simulation, not validated on physical silicon.** Synthesis/place-and-route, timing closure, clock tolerance, physical reset debounce, asynchronous-input metastability hardening, board wiring, fault injection, and the stubbed UART TX path remain outside the retained simulation result.
- **The latch timing requirement is not yet semantically frozen.** 680.01 µs is an observed simulation result, not evidence that a 670 µs requirement is satisfied until the inequality/direction and measurement boundary are defined.
- **Chronicle is tamper-evident, not tamper-proof.** A full-file forward recomputation is only detectable against an anchor or witness state the attacker cannot rewrite.
- Local passing tests are not independent reproduction, operational validation, certification, or production authority.

## Status

| Artifact | Retained local result | Defensible scope | Still needed |
|---|---:|---|---|
| Lucifer Latch | 8/8 simulation checks | exact RTL/testbench behavior in Icarus simulation | freeze timing contract; synth/P&R; CDC/metastability/debounce; physical board evidence; independent reproduction |
| Chronicle | 15/15 adversarial checks | tested tamper-evidence/anchor logic | external anchor/witness implementation; fresh/independent reproduction |

## Core evidence rule

```text
simulation != silicon
passing_test != universal proof
hash_chain != immutable storage
local_reproduction != independent_reproduction
capability != authority
```

## License

MIT.
