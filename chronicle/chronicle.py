"""
chronicle.py — Tamper-evident, append-only, SHA-256 hash-chained ledger.

This is a real implementation of the "Immutable Memory" invariant: every entry
is cryptographically linked to the one before it. Altering, reordering, deleting,
or inserting any entry breaks the chain, and verify() detects it.

Contrast with a "visual-effect" hash: this uses SHA-256 over a canonical
serialization and ships a verifier. Tamper-evidence is the whole point, so it
is tested adversarially in test_chronicle.py.

Note on threat model: a hash chain is tamper-EVIDENT, not tamper-PROOF. An
attacker who can rewrite the entire file can recompute every hash forward from
the tampered entry. Defenses against that (external anchoring of the head hash,
append-only/WORM storage, signatures) are noted in the report — this module
gives you the detection primitive they all build on.
"""
from __future__ import annotations
import hashlib, json, math, os, re, threading, time
from dataclasses import dataclass, asdict
from typing import Any

GENESIS_PREV = "0" * 64  # prev_hash of the first block

def _canonical(obj: Any) -> bytes:
    # Deterministic serialization: sorted keys, no whitespace ambiguity.
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def compute_hash(index: int, timestamp: float, payload: dict, prev_hash: str) -> str:
    h = hashlib.sha256()
    h.update(_canonical({"index": index, "timestamp": timestamp,
                         "payload": payload, "prev_hash": prev_hash}))
    return h.hexdigest()

@dataclass
class Entry:
    index: int
    timestamp: float
    payload: dict
    prev_hash: str
    hash: str
    def to_dict(self): return asdict(self)

class Chronicle:
    def __init__(self, path: str | None = None):
        self.path = path
        self.entries: list[Entry] = []
        self._append_lock = threading.RLock()  # same-object threads only, not cross-process
        self._uncertain_persist = False
        if path and os.path.exists(path):
            self._load()

    def append(self, payload: dict, timestamp: float | None = None) -> Entry:
        """Append only on a locally verified chain and unchanged disk snapshot.

        This is not cross-process locking or crash-atomic storage. An ambiguous
        write permanently poisons this instance; reopen and verify the ledger
        before further work. External authenticated anchoring is still absent.
        """
        with self._append_lock:
            if self._uncertain_persist:
                raise RuntimeError("previous persistence outcome unknown; reopen and verify")
            valid, detail = self.verify()
            if not valid:
                raise ValueError(f"existing ledger invalid; append refused: {detail}")
            if self.path:
                self._assert_disk_unchanged()

            ts = time.time() if timestamp is None else timestamp
            if type(ts) not in (int, float) or not math.isfinite(ts):
                raise ValueError("timestamp must be a finite number")
            if not isinstance(payload, dict):
                raise TypeError("payload must be a JSON object")
            # Immutable value snapshot: do not retain caller-owned nested objects.
            # Strict canonicalization rejects nonfinite JSON values.
            frozen_payload = json.loads(_canonical(payload))
            idx = len(self.entries)
            prev = self.entries[-1].hash if self.entries else GENESIS_PREV
            e = Entry(idx, ts, frozen_payload,
                      prev, compute_hash(idx, ts, frozen_payload, prev))
            if self.path:
                try:
                    with open(self.path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(e.to_dict(), allow_nan=False) + "\n")
                        f.flush()
                        os.fsync(f.fileno())
                except OSError:
                    # The disk may contain part/all of the entry even if the
                    # caller saw an exception. Never retry on this instance.
                    self._uncertain_persist = True
                    raise
            self.entries.append(e)
            return e

    def _assert_disk_unchanged(self) -> None:
        if not os.path.exists(self.path):
            if self.entries:
                raise ValueError("ledger file disappeared since last read")
            return
        disk = Chronicle(self.path)
        valid, reason = disk.verify()
        if not valid:
            raise ValueError(f"on-disk chain invalid: {reason}")
        if len(disk.entries) != len(self.entries) or disk.head() != self.head():
            raise ValueError("on-disk head changed since last read")

    def _load(self):
        def unique_keys(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f"duplicate Chronicle JSON key: {key}")
                result[key] = value
            return result

        def nonfinite(value):
            raise ValueError(f"nonfinite Chronicle JSON value: {value}")

        fields = {"index", "timestamp", "payload", "prev_hash", "hash"}
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    d = json.loads(line, object_pairs_hook=unique_keys,
                                   parse_constant=nonfinite)
                    if not isinstance(d, dict) or set(d) != fields:
                        raise ValueError("invalid Chronicle entry schema")
                    self.entries.append(Entry(**d))

    def verify(self) -> tuple[bool, str]:
        """Walk the chain. Returns (ok, message). Detects ANY tampering."""
        prev = GENESIS_PREV
        for i, e in enumerate(self.entries):
            if e.index != i:
                return False, f"index mismatch at position {i}: stored index={e.index}"
            if e.prev_hash != prev:
                return False, f"broken link at index {i}: prev_hash does not match prior hash"
            try:
                recomputed = compute_hash(e.index, e.timestamp, e.payload, e.prev_hash)
            except (ValueError, TypeError, OverflowError) as exc:
                return False, f"invalid entry at index {i}: {exc}"
            if recomputed != e.hash:
                return False, f"content tampered at index {i}: hash != recomputed hash"
            prev = e.hash
        return True, f"chain valid: {len(self.entries)} entries, head={prev[:16]}..."

    def head(self) -> str:
        return self.entries[-1].hash if self.entries else GENESIS_PREV

    def merkle_root(self) -> str:
        """Merkle root over entry hashes (enables compact inclusion proofs)."""
        layer = [bytes.fromhex(e.hash) for e in self.entries]
        if not layer:
            return GENESIS_PREV
        while len(layer) > 1:
            if len(layer) % 2: layer.append(layer[-1])  # duplicate last if odd
            layer = [hashlib.sha256(layer[i] + layer[i+1]).digest()
                     for i in range(0, len(layer), 2)]
        return layer[0].hex()


# --- Head anchoring: closes the truncation/rewrite gap when anchor is trusted ---
def make_anchor(chron: "Chronicle") -> dict:
    """Snapshot the chain head. Publish this to an EXTERNAL append-only store
    (or have witnesses co-sign it). Truncation/rewrite then becomes detectable."""
    return {"count": len(chron.entries), "head": chron.head(),
            "merkle_root": chron.merkle_root()}

def verify_against_anchor(chron: "Chronicle", anchor: dict) -> tuple[bool, str]:
    if not isinstance(anchor, dict) or set(anchor) != {"count", "head", "merkle_root"}:
        return False, "malformed anchor schema"
    if type(anchor["count"]) is not int or anchor["count"] < 0:
        return False, "malformed anchor count"
    if any(not isinstance(anchor[k], str) or
           re.fullmatch(r"[0-9a-f]{64}", anchor[k]) is None
           for k in ("head", "merkle_root")):
        return False, "malformed anchor digest"
    ok, msg = chron.verify()
    if not ok:
        return False, msg
    if len(chron.entries) != anchor["count"]:
        return False, (f"entry count {len(chron.entries)} != anchored {anchor['count']} "
                       f"(truncation/insertion detected)")
    if chron.head() != anchor["head"]:
        return False, "head hash != anchored head (rewrite detected)"
    if chron.merkle_root() != anchor["merkle_root"]:
        return False, "merkle root != anchored root (content rewrite detected)"
    return True, f"verified against anchor: {anchor['count']} entries, head matches"
