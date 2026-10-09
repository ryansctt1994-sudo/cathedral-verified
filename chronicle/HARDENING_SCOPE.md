# P0-002: Chronicle append-safety review candidate

## Pinned starting point

- Base `main`: `1c4181714b48dd9d9616a0bebbb4fef8532deff8`
- Original `chronicle/chronicle.py` Git blob: `ad2366444540e1f31e1c5513b4f141af06bc7502`
- This is a review-only source change, not a production promotion.

## Changes and reproducible checks

1. Refuse append when the current in-memory chain fails self-verification.
2. Compare the disk ledger chain/head/count with the in-memory view before append. Refuse detected drift, file deletion, or on-disk damage.
3. Append to memory only after the disk write and `fsync` return. A failed write leaves the instance poisoned; its durable outcome is unknown until re-open and inspection.
4. Copy the payload before hashing to break caller-owned object aliasing. Reject nonfinite timestamps and nonstandard JSON values, duplicate on-disk JSON keys, and unexpected top-level entry fields.
5. Return explicit refusals on malformed anchor snapshots instead of allowing exceptions to escape.
6. Make the existing manual Chronicle test script fail CI with a nonzero exit when checks fail. Execute ten added `unittest` methods in CI.

```bash
cd chronicle
python3 test_chronicle.py
python3 -m unittest -v test_chronicle_hardening
```

## Known limitations — these are release blockers

- The file is **not crash-atomic**: a failed or interrupted write can leave an incomplete JSONL line. No recovery journal or automatic rollback is provided.
- There is **no cross-process/file lock**, no protection from an adversary swapping a file between the disk check and subsequent open/write, and no detection of a malicious writer rewriting both file and local anchor. `RLock` covers same-instance threads only.
- The full-chain check on every append is O(n) per append; constructing a large journal is O(n²). Benchmark/replace before heavy workloads.
- Validating a caller-supplied anchor proves no external trust. This patch adds **no trusted signature, witness, independently anchored log, permission boundary, hardware veto, RFC9162 compatibility, or production authorization**.
- Historical tests are a bounded test suite, not a cryptographic security proof.

**Portfolio: E2 | W0 | O0 WITHHELD | PRODUCTION PROHIBITED.**
