"""Adversarial test suite for chronicle.py — tries to BREAK tamper-evidence."""
import copy, json, os, tempfile
from chronicle import Chronicle, compute_hash, GENESIS_PREV

P, F = 0, 0
def check(cond, name):
    global P, F
    if cond: P += 1; print(f"  PASS: {name}")
    else:    F += 1; print(f"  FAIL: {name}")

def fresh(n=5):
    c = Chronicle()
    for i in range(n):
        c.append({"event": f"action_{i}", "actor": "L0:Steward", "value": i})
    return c

print("[T1] Honest chain verifies")
c = fresh()
ok, msg = c.verify(); check(ok, f"clean 5-entry chain valid ({msg})")

print("[T2] Tamper a payload field -> detected")
c = fresh(); c.entries[2].payload["value"] = 999
ok, msg = c.verify(); check(not ok and "index 2" in msg, f"middle-entry edit caught ({msg})")

print("[T3] Tamper + recompute that ONE entry's hash -> still detected (chain break)")
c = fresh()
c.entries[2].payload["value"] = 999
c.entries[2].hash = compute_hash(2, c.entries[2].timestamp, c.entries[2].payload, c.entries[2].prev_hash)
ok, msg = c.verify()
check(not ok, f"local re-hash still breaks downstream link ({msg})")

print("[T4] Reorder two entries -> detected")
c = fresh(); c.entries[1], c.entries[3] = c.entries[3], c.entries[1]
ok, msg = c.verify(); check(not ok, f"reordering caught ({msg})")

print("[T5] Delete an entry -> detected")
c = fresh(); del c.entries[2]
ok, msg = c.verify(); check(not ok, f"deletion caught ({msg})")

print("[T6] Truncate the tail -> chain still self-consistent (expected) but head changes")
c = fresh(); full_head = c.head(); c.entries = c.entries[:3]
ok, _ = c.verify(); check(ok, "truncated chain is internally valid (why external anchoring is needed)")
check(c.head() != full_head, "truncation changes head hash (detectable IF head is anchored)")

print("[T7] Insert a forged entry in the middle -> detected")
c = fresh()
forged = copy.deepcopy(c.entries[2]); forged.payload = {"event": "FORGED", "actor": "attacker", "value": -1}
c.entries.insert(2, forged)
ok, msg = c.verify(); check(not ok, f"inserted forged entry caught ({msg})")

print("[T8] Persistence round-trip: write to disk, reload, verify")
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "chronicle.jsonl")
    c = Chronicle(path)
    for i in range(10): c.append({"event": f"persisted_{i}", "value": i})
    head_before = c.head()
    c2 = Chronicle(path)                      # reload from disk
    ok, msg = c2.verify()
    check(ok and c2.head() == head_before, f"reloaded chain verifies & head matches ({msg})")

print("[T9] On-disk tamper: edit the JSONL file, reload -> detected")
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "chronicle.jsonl")
    c = Chronicle(path)
    for i in range(5): c.append({"event": f"e{i}", "value": i})
    lines = open(path).read().splitlines()
    rec = json.loads(lines[2]); rec["payload"]["value"] = 7777   # tamper file directly
    lines[2] = json.dumps(rec); open(path, "w").write("\n".join(lines) + "\n")
    c3 = Chronicle(path); ok, msg = c3.verify()
    check(not ok, f"file-level tamper caught on reload ({msg})")

print("[T10] Merkle root is deterministic and content-sensitive")
def build(values, ts0=1000.0):
    c = Chronicle()
    for i, v in enumerate(values):
        c.append({"event": f"action_{i}", "actor": "L0:Steward", "value": v}, timestamp=ts0+i)
    return c
r1 = build([0,1,2,3,4]).merkle_root()
r2 = build([0,1,2,3,4]).merkle_root()          # same content + same timestamps
check(r1 == r2, "identical content -> identical merkle root (deterministic)")
r3 = build([0,1,2,3,99]).merkle_root()         # one field changed
check(r3 != r1, "any change -> different merkle root")


print("[T11] Head-anchoring closes the truncation gap (T6)")
from chronicle import make_anchor, verify_against_anchor
def build2(values, ts0=2000.0):
    c = Chronicle()
    for i, v in enumerate(values):
        c.append({"event": f"e{i}", "value": v}, timestamp=ts0+i)
    return c
c = build2([0,1,2,3,4,5,6])
anchor = make_anchor(c)                      # <-- publish externally
ok, msg = verify_against_anchor(c, anchor); check(ok, f"untouched chain matches anchor ({msg})")
c.entries = c.entries[:4]                     # truncate (was UNDETECTED in T6)
ok, msg = verify_against_anchor(c, anchor)
check(not ok and "truncation" in msg, f"truncation now DETECTED via anchor ({msg})")

print("[T12] Full forward-recompute rewrite is caught by anchor")
c2 = build2([9,9,9])                          # attacker rebuilds a clean-looking chain
ok, _ = c2.verify()                            # internally valid...
anchor_real = make_anchor(build2([0,1,2]))     # ...but doesn't match the real anchor
ok2, msg = verify_against_anchor(c2, anchor_real)
check(ok and not ok2, f"rewritten chain verifies internally but fails anchor ({msg})")

print(f"\n================ RESULT ================")
print(f"  PASSED: {P}   FAILED: {F}")
print(f"=======================================")
print("  VERDICT: TAMPER-EVIDENCE VERIFIED" if F == 0 else "  VERDICT: FAILURES — SEE ABOVE")
