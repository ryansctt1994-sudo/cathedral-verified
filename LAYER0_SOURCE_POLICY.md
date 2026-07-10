# Layer 0 Source Policy

## Status

Implemented as a bounded repository input gate on `agent/p0-repair-regressions`.

This layer rejects files that are clearly binary, precompiled, packaged, or otherwise opaque before they are admitted as repository source inputs.

## Invariants

- `INV-BOOT-001`: Forbidden opaque or precompiled artifacts must be rejected.
- `INV-BOOT-002`: Unreadable repository inputs must fail closed.

## Enforced indicators

The gate checks for:

- forbidden compiled and packaged suffixes such as `.o`, `.so`, `.dll`, `.exe`, `.jar`, `.wasm`, `.whl`, and `.zip`
- forbidden generated executable names such as `a.out` and `sim_latch`
- binary NUL bytes
- known ELF, PE, ZIP, Java class, and WebAssembly signatures

## Guardian tests

- `test_blob_breaks_noBlobs`
- `test_blobTool_rejected`
- human-readable source acceptance
- forbidden-extension rejection without relying on magic bytes

## Commands

```bash
PYTHONPATH=src:. python3 -m unittest tests.test_bootstrap -v
make test-bootstrap
make test
```

## Evidence boundary

This policy establishes repository-level rejection of obvious opaque or precompiled inputs under the implemented rules.

It does **not** establish:

- a GNU Mes-style full source bootstrap
- compiler or interpreter provenance
- reproducible toolchain construction
- diverse double compilation
- elimination of the Trusting Trust problem
- source-to-silicon physical verification

Those remain separate promotion gates requiring dedicated source bootstrap scripts, pinned toolchain sources, build receipts, binary comparisons, and external reproduction.

## Current receipt

```text
Validated implementation head: 40449d33e45dfc1c60b82e08d511738a81eacb32
GitHub Actions run: #19
Layer 0 source-policy checks: PASS
Chronicle verification: PASS
P0 regression suite: PASS
Lucifer Latch RTL simulation: PASS
```
