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
import hashlib, json, os, time
from dataclasses import dataclass, asdict
from typing import Any

GENESIS_PREV = "0" * 64  # prev_hash of the first block

def _canonical(obj: Any) -> bytes:
    # Deterministic serialization: sorted keys, no whitespace ambiguity.
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")

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
        if path and os.path.exists(path):
            self._load()

    def append(self, payload: dict, timestamp: float | None = None) -> Entry:
        ts = time.time() if timestamp is None else timestamp
        idx = len(self.entries)
        prev = self.entries[-1].hash if self.entries else GENESIS_PREV
        h = compute_hash(idx, ts, payload, prev)
        e = Entry(idx, ts, payload, prev, h)
        self.entries.append(e)
        if self.path:
            with open(self.path, "a") as f:
                f.write(json.dumps(e.to_dict()) + "\n")
                f.flush(); os.fsync(f.fileno())   # durability: survive crash
        return e

    def _load(self):
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if line:
                    d = json.loads(line)
                    self.entries.append(Entry(**d))

    def verify(self) -> tuple[bool, str]:
        """Walk the chain. Returns (ok, message). Detects ANY tampering."""
        prev = GENESIS_PREV
        for i, e in enumerate(self.entries):
            if e.index != i:
                return False, f"index mismatch at position {i}: stored index={e.index}"
            if e.prev_hash != prev:
                return False, f"broken link at index {i}: prev_hash does not match prior hash"
            recomputed = compute_hash(e.index, e.timestamp, e.payload, e.prev_hash)
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
