# cathedral-verified

Two safety primitives with **passing, reproducible test suites**. Nothing here is
asserted on trust — clone it and run `make test`. If a claim isn't backed by a test
in this repo, it isn't claimed here.

## What's verified

### 1. Lucifer Latch — hardware safety veto (`hardware/lucifer_latch/`)
An irreversible FPGA kill switch (Verilog, Artix-7 / Arty A7-35T target). Simulated
with Icarus Verilog; **8/8 checks pass.** The property that matters — once tripped,
**no software input clears it; only physical reset does** — is proven by hammering it
with max threat + trigger toggling and confirming it stays latched. Timing floor
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

## Status
| Artifact | Checks | Verified scope | Still needed |
|----------|:------:|----------------|--------------|
| Lucifer Latch | 8/8 | RTL behavior in sim | silicon: synth, debounce, metastability, UART TX |
| Chronicle | 15/15 | tamper-evidence + anchoring logic | external anchor store / witness quorum |

## License
MIT.
