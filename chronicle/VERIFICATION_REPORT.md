# Chronicle — Verification Report

**Module:** `chronicle.py`  
**Date:** 2026-06-22  
**Tool:** Python 3 + stdlib `hashlib`  
**Status:** ✅ 15/15 adversarial checks pass

Reproduce:

```bash
python3 test_chronicle.py
```

---

## Why this exists

The project requires an actual tamper-evident memory primitive, not a visual or symbolic hash chain.

This module implements a SHA-256 hash-chained append-only ledger using deterministic canonical serialization and a verifier. The adversarial test suite attacks the chain directly.

If tampering is detected, the verifier fails.

---

## What was verified

| # | Attack / Property | Outcome |
|---|---|---|
| T1 | Honest 5-entry chain | verifies ✓ |
| T2 | Edit a payload field mid-chain | detected ✓ |
| T3 | Edit + locally re-hash one entry | detected by downstream chain break ✓ |
| T4 | Reorder two entries | detected ✓ |
| T5 | Delete an entry | detected ✓ |
| T6 | Truncate the tail | internally valid, but head changes ✓ |
| T7 | Insert a forged entry | detected ✓ |
| T8 | Write to disk, reload, verify | round-trip succeeds ✓ |
| T9 | Tamper JSONL file directly, reload | detected ✓ |
| T10 | Merkle root determinism + sensitivity | verified ✓ |
| T11 | Head-anchoring closes truncation gap | detected when anchored ✓ |
| T12 | Full forward-recompute rewrite | internally valid, but caught by anchor ✓ |

Total checks: **15 passed, 0 failed**

---

## The important boundary

A hash chain is **tamper-evident**, not automatically tamper-proof.

Without an external anchor, a full-file rewrite can recompute every hash forward and produce a self-consistent rewritten chain.

This repo closes that detection gap at the primitive level by supporting head anchoring:

- An untouched chain matches its anchor.
- A truncated chain fails against the anchor.
- A full forward-recompute rewrite fails against the anchor.

The remaining real-world requirement is to store the anchor somewhere the attacker cannot also rewrite, such as:

- an external append-only store,
- a witness quorum,
- signed publication,
- or another independent anchoring surface.

This repo implements the local detection primitive and anchor check. It does not implement the external anchor store.

---

## Files

- `chronicle.py` — SHA-256 chain, canonical serialization, `verify()`, `head()`, `merkle_root()`, anchor verification
- `test_chronicle.py` — 15-check adversarial suite
- `test_results.log` — captured run output showing 15/15 pass

---

## What production hardening would add

- External head-anchor publication
- Per-entry signatures
- WORM / append-only storage policy
- Monotonic sequence or clock guarantees
- Independent witness storage
