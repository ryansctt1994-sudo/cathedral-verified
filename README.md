# cathedral-verified

Two bounded safety primitives with repository-local tests. The repository is designed for reproducibility, but a green local or GitHub CI run is **not** the same as independent reproduction or production certification.

Nothing broader than the exercised test scope is claimed here.

## What's verified

### 1. Lucifer Latch — hardware safety veto (`hardware/lucifer_latch/`)
An irreversible FPGA kill switch (Verilog, Artix-7 / Arty A7-35T target). Simulated
with Icarus Verilog; **8/8 checks pass.** The property that matters — once tripped,
**no software input clears it; only physical reset does** — is tested in RTL simulation by exercising max-threat and trigger toggling and confirming the simulated latch remains set. Timing floor
measured at 68001 cycles ≈ 680 µs @100 MHz, on spec.

### 2. Chronicle — tamper-evident ledger (`chronicle/`)
A SHA-256 hash-chained append-only log (Python stdlib only). **15/15 adversarial checks
pass.** Field edits, re-hashing, reordering, deletion, forged inserts, and on-disk
tampering are all detected. Head-anchoring closes the truncation/rewrite gap.

## Reproduce
```bash
make test          # runs both suites
# or individually:
make test-chronicle
make test-hw        # requires: iverilog
```
The GitHub Actions workflow currently runs the Chronicle verification suite on every push.
Run `make test` locally for the full Chronicle + Lucifer Latch check until hardware-simulation CI is expanded.

## What is NOT claimed (read this)
Honesty is the point of this repo, so the limits are stated up front:

- **The latch is verified in *simulation*, not on silicon.** Synthesis timing closure,
  physical button debounce, async-input metastability hardening, and the (currently
  stubbed) UART TX path are all still required before a board flash means anything.
- **The chronicle is tamper-*evident*, not tamper-*proof*.** Detecting a full-file
  forward-recompute rewrite requires the anchor (head hash) to live somewhere the
  attacker can't also rewrite — an external append-only store or a quorum of witnesses.
  The repo implements the detection primitive and the anchor mechanism; it does not
  implement the external store. That's the next real step, not a solved one.

## Independence boundary

GitHub Actions success demonstrates that the configured workflow passed in GitHub's environment for that commit. It does not establish clean-room independent reproduction, silicon behavior, external witness anchoring, or production safety.

## Status
| Artifact | Checks | Verified scope | Still needed |
|----------|:------:|----------------|--------------|
| Lucifer Latch | 8/8 | RTL behavior in sim | silicon: synth, debounce, metastability, UART TX |
| Chronicle | 15/15 | tamper-evidence + anchoring logic | external anchor store / witness quorum |

## License
MIT.
