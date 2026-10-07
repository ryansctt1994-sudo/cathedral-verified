# cathedral-verified

Two bounded safety primitives with repository-local tests. A passing local or GitHub
Actions run is evidence about the exercised revision and command; it is **not**
independent reproduction, production certification, or deployment authority.

Nothing broader than the explicitly exercised test scope is claimed here.

## What's verified

### 1. Lucifer Latch — hardware safety veto (`hardware/lucifer_latch/`)
An irreversible FPGA kill switch (Verilog, Artix-7 / Arty A7-35T target). The
repository's historical RTL simulation suite reports **8/8 checks pass**. The tested
property is that once tripped, software inputs do not clear the simulated latch;
physical reset is required. This is simulation evidence only — not silicon validation,
synthesis timing closure, or board-measured behavior. The PR #4 hosted run discussed
below does not rerun this hardware suite.

### 2. Chronicle — tamper-evident ledger (`chronicle/`)
A SHA-256 hash-chained tamper-evident log (Python stdlib only). On PR #4 at
`6f6e6b78a2d6439d719fa406612387808db4899b`, the repaired command executed
**12 pytest tests and passed** in GitHub Actions run
[37652321891](https://github.com/ryansctt1994-sudo/cathedral-verified/actions/runs/37652321891).
The repair also demonstrated that the former workflow command could exit successfully
without executing the pytest test functions; the corrected target fails closed on a
deliberately failing test.

Older 15/15 Chronicle counts are retained only as historical reports. The current
bounded claim is the repaired 12-test execution at the exact PR revision above.

## Reproduce
```bash
make test          # runs both suites
# or individually:
make test-chronicle
make test-hw        # requires: iverilog
```
The PR #4 workflow runs the Chronicle pytest suite on GitHub Actions with read-only
repository permissions and a bounded timeout. Run `make test` locally for the
combined Chronicle + Lucifer Latch suite until hardware-simulation CI is expanded.

A green hosted run remains same-project CI. It does not establish a qualifying
independent witness.

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
| Lucifer Latch | historical 8/8 report | RTL behavior in simulation | fresh hosted rerun; synthesis; silicon; debounce; metastability; UART TX |
| Chronicle | 12 pytest tests on PR #4 | bounded tamper-detection behavior exercised by the repaired command | merge/review decision; external anchor store / witness quorum; independent reproduction |

## Evidence boundary

- **Hosted PR evidence:** PASS for the exact PR #4 revision named above.
- **Independent reproduction:** not established.
- **Witness:** W0 at portfolio level.
- **Operational authority:** O0 — withheld.
- **Production:** prohibited by the portfolio governance posture.

## License
MIT.
