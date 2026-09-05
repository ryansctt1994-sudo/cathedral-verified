# C-002A — Local Chronicle Tamper Detection

## Claim

The Chronicle implementation detects the following modifications to a local SHA-256 hash-chained event log:

- payload modification;
- deletion of a non-tail entry;
- entry reordering;
- middle insertion;
- direct on-disk record modification;
- tail truncation when compared with a previously captured anchor;
- complete forward-chain reconstruction when compared with a previously captured anchor.

## Non-claims

This artifact does not establish:

- mutation prevention;
- operating-system or storage-level append-only enforcement;
- WORM storage;
- an independent remote anchor;
- resistance when one actor controls both the log and anchor;
- independent reproduction;
- production readiness.

The local chain is tamper-evident, not tamper-proof.

## Run

```bash
python3 -m pip install -r requirements-dev.txt
make test-chronicle
```

A failed assertion must produce a nonzero process exit status.

## Evidence boundary

Current target: local E2 execution evidence.

Promotion beyond E2 requires an exact revision, environment manifest, raw logs, file hashes, and an independent execution receipt.
