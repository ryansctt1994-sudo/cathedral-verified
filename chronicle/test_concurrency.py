"""Local Linux cooperating-writer invariants; no external witness claim."""
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

import pytest
from hypothesis import given, settings, strategies as st

from chronicle import Chronicle, make_anchor, verify_against_anchor


def _append_worker(path, worker, barrier):
    ledger = Chronicle(path)
    barrier.wait(timeout=20)
    for sequence in range(20):
        ledger.append({'worker': worker, 'sequence': sequence})


def test_process_writers_preserve_every_entry(tmp_path):
    path = str(tmp_path / 'chronicle.jsonl')
    ctx = mp.get_context('spawn')
    with ctx.Manager() as manager:
        barrier = manager.Barrier(6)
        with ProcessPoolExecutor(6, mp_context=ctx) as pool:
            jobs = [pool.submit(_append_worker, path, i, barrier) for i in range(6)]
            for job in jobs:
                job.result(timeout=60)
    ledger = Chronicle(path)
    assert ledger.verify()[0]
    assert len(ledger.entries) == 120
    assert {(e.payload['worker'], e.payload['sequence']) for e in ledger.entries} == {
        (i, j) for i in range(6) for j in range(20)
    }


def test_stale_instances_extend_current_disk_head(tmp_path):
    path = str(tmp_path / 'ledger.jsonl')
    first, stale = Chronicle(path), Chronicle(path)
    first.append({'first': True})
    stale.append({'second': True})
    assert Chronicle(path).verify()[0]


def test_refuses_corrupt_or_partial_tail_without_writing(tmp_path):
    path = tmp_path / 'ledger.jsonl'
    ledger = Chronicle(str(path))
    ledger.append({'valid': True})
    path.write_bytes(path.read_bytes() + b'{"index":')
    before = path.read_bytes()
    with pytest.raises(ValueError):
        ledger.append({'must_not_write': True})
    assert path.read_bytes() == before


@settings(max_examples=50, deadline=None)
@given(st.lists(st.integers(), min_size=1, max_size=40))
def test_generated_payloads_and_tamper_detection(values):
    ledger = Chronicle()
    for i, value in enumerate(values):
        ledger.append({'value': value}, timestamp=float(i))
    anchor = make_anchor(ledger)
    assert ledger.verify()[0]
    assert verify_against_anchor(ledger, anchor)[0]
    ledger.entries[len(values) // 2].payload['value'] += 1
    assert not ledger.verify()[0]


@settings(max_examples=40, deadline=None)
@given(st.lists(st.integers(), min_size=1, max_size=30), st.data())
def test_generated_prefix_truncation_requires_anchor(values, data):
    ledger = Chronicle()
    for i, value in enumerate(values):
        ledger.append({'value': value}, timestamp=float(i))
    anchor = make_anchor(ledger)
    cut = data.draw(st.integers(min_value=0, max_value=len(values) - 1))
    ledger.entries = ledger.entries[:cut]
    assert ledger.verify()[0]  # Internal hashing alone cannot detect tail removal.
    assert not verify_against_anchor(ledger, anchor)[0]
