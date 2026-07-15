"""Pytest suite for Chronicle tamper-evidence and persistence behavior."""

import copy
import json
import os
import tempfile

from chronicle import Chronicle
from chronicle import compute_hash
from chronicle import make_anchor
from chronicle import verify_against_anchor


def fresh(count: int = 5) -> Chronicle:
    chronicle = Chronicle()
    for index in range(count):
        chronicle.append(
            {
                "event": f"action_{index}",
                "actor": "L0:Steward",
                "value": index,
            },
            timestamp=1000.0 + index,
        )
    return chronicle


def build(values: list[int], timestamp_start: float = 2000.0) -> Chronicle:
    chronicle = Chronicle()
    for index, value in enumerate(values):
        chronicle.append(
            {
                "event": f"event_{index}",
                "value": value,
            },
            timestamp=timestamp_start + index,
        )
    return chronicle


def test_honest_chain_verifies() -> None:
    chronicle = fresh()
    valid, message = chronicle.verify()

    assert valid, message


def test_payload_tampering_is_detected() -> None:
    chronicle = fresh()
    chronicle.entries[2].payload["value"] = 999

    valid, message = chronicle.verify()

    assert not valid
    assert "index 2" in message


def test_local_rehash_still_breaks_downstream_link() -> None:
    chronicle = fresh()
    entry = chronicle.entries[2]
    entry.payload["value"] = 999
    entry.hash = compute_hash(
        entry.index,
        entry.timestamp,
        entry.payload,
        entry.prev_hash,
    )

    valid, _ = chronicle.verify()

    assert not valid


def test_reordering_is_detected() -> None:
    chronicle = fresh()
    chronicle.entries[1], chronicle.entries[3] = (
        chronicle.entries[3],
        chronicle.entries[1],
    )

    valid, _ = chronicle.verify()

    assert not valid


def test_deletion_is_detected() -> None:
    chronicle = fresh()
    del chronicle.entries[2]

    valid, _ = chronicle.verify()

    assert not valid


def test_tail_truncation_requires_external_anchor() -> None:
    chronicle = fresh()
    full_head = chronicle.head()
    chronicle.entries = chronicle.entries[:3]

    valid, _ = chronicle.verify()

    assert valid
    assert chronicle.head() != full_head


def test_middle_insertion_is_detected() -> None:
    chronicle = fresh()
    forged = copy.deepcopy(chronicle.entries[2])
    forged.payload = {
        "event": "FORGED",
        "actor": "attacker",
        "value": -1,
    }
    chronicle.entries.insert(2, forged)

    valid, _ = chronicle.verify()

    assert not valid


def test_persistence_round_trip_preserves_head() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "chronicle.jsonl")
        original = Chronicle(path)
        for index in range(10):
            original.append(
                {
                    "event": f"persisted_{index}",
                    "value": index,
                },
                timestamp=3000.0 + index,
            )

        head_before = original.head()
        reloaded = Chronicle(path)
        valid, message = reloaded.verify()

        assert valid, message
        assert reloaded.head() == head_before


def test_on_disk_tampering_is_detected_after_reload() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "chronicle.jsonl")
        chronicle = Chronicle(path)
        for index in range(5):
            chronicle.append(
                {
                    "event": f"event_{index}",
                    "value": index,
                },
                timestamp=4000.0 + index,
            )

        with open(path, encoding="utf-8") as handle:
            lines = handle.read().splitlines()

        record = json.loads(lines[2])
        record["payload"]["value"] = 7777
        lines[2] = json.dumps(record)

        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")

        reloaded = Chronicle(path)
        valid, _ = reloaded.verify()

        assert not valid


def test_merkle_root_is_deterministic_and_content_sensitive() -> None:
    first = build([0, 1, 2, 3, 4]).merkle_root()
    second = build([0, 1, 2, 3, 4]).merkle_root()
    changed = build([0, 1, 2, 3, 99]).merkle_root()

    assert first == second
    assert changed != first


def test_anchor_detects_truncation() -> None:
    chronicle = build([0, 1, 2, 3, 4, 5, 6])
    anchor = make_anchor(chronicle)

    valid_before, message_before = verify_against_anchor(chronicle, anchor)
    assert valid_before, message_before

    chronicle.entries = chronicle.entries[:4]
    valid_after, message_after = verify_against_anchor(chronicle, anchor)

    assert not valid_after
    assert "truncation" in message_after


def test_anchor_detects_full_forward_rewrite() -> None:
    rewritten = build([9, 9, 9])
    authentic = build([0, 1, 2])
    authentic_anchor = make_anchor(authentic)

    internally_valid, internal_message = rewritten.verify()
    anchor_valid, anchor_message = verify_against_anchor(
        rewritten,
        authentic_anchor,
    )

    assert internally_valid, internal_message
    assert not anchor_valid, anchor_message
