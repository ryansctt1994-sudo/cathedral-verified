# CATHEDRAL FORGE

## External Engineering Review Package

**Version:** 6.1 Canonical  
**Date:** 2026-07-10  
**Steward:** Ryan Scott  
**Repository:** `ryansctt1994-sudo/cathedral-verified`  
**Review target:** Pull Request #1  
**Review branch:** `agent/p0-repair-regressions`  
**Pinned validated implementation commit:** `8ab93420b6ce86c66834d697aabc6a672ba0ec73`  
**Validated workflow:** GitHub Actions run #47

> Everything claimed in this package must be independently recoverable from repository source, CI evidence, or an explicit future-work declaration.

---

## 1. Executive Summary

Cathedral Forge is an integrated prototype for evidence-governed AI runtime control. It does not attempt to replace or improve a foundation model. It constrains how proposed actions, model outputs, evidence, and hardware-adjacent safety signals may influence authority and persistent state.

The current review branch emphasizes:

- fail-closed policy behavior
- typed and bounded input recognition
- explicit evidence boundaries
- append-only provenance through Chronicle
- regression and adversarial testing
- classifier-confidence containment
- source-tree rejection of obvious opaque artifacts
- RTL simulation of an irreversible latch property

The package should be reviewed as governance and verification infrastructure. It is not presented as a production AI platform, independently validated safety system, or physically verified FPGA implementation.

---

## 2. Repository and Branch Distinction

### `main`

The default branch contains the narrower foundational baseline, including:

- Chronicle append-only hash-chained ledger
- Lucifer Latch RTL and testbench
- supporting documentation and CI history

### Pull Request #1

PR #1 is the integrated review candidate. It adds:

- the Cathedral Forge orchestration scaffold
- P0 safety and consistency repairs
- complete Chronicle receipt integration
- Layer 0 repository source policy
- Weaver Recognition Kernel and LANGSEC doctrine
- Classifier Assurance Gate
- expanded Python and RTL CI validation

The review target is PR #1, not an inferred capability of `main`.

---

## 3. Current Evidence Posture

| Layer | Current status | Evidence boundary |
|---|---|---|
| Architecture and source descriptions | E1 | Source and documentation exist |
| Integrated repair branch | E2 repository/CI candidate | Exact commit executed successfully in repository CI |
| Recognition assurance | P3 | Grammar and bounds documented, canonical parser implemented, malformed-input tests pass |
| Classifier assurance scaffold | Repository/CI verified | Gate and toy spoof-search regression pass; domain calibration not established |
| Independent external reproduction | Absent | Required for full external promotion |
| Physical FPGA verification | Absent | RTL simulation only |
| Production authority | NONE / HOLD | Explicitly withheld |

CI success does not transfer authority to untested layers.

---

## 4. Implemented Review Scope

### 4.1 Cathedral Forge P0 repair core

Primary artifacts:

- `src/cathedral_forge_final.py`
- `tests/test_p0_regressions.py`

Implemented behaviors include:

- approval text derives from the canonical approval property
- unavailable hardware fails closed
- BLOCK raises simulated threat level and invokes the latch transport
- HEVA health is derived from transport readback
- alpha-plus-omega conservation is executable rather than decorative
- unknown extraction input abstains instead of becoming KEEP
- response-quality evaluation is separated from semantic safety classification
- Chronicle entries populate the Cathedral L5 ledger
- Neural Cosmos executes during orchestration
- the 680 microsecond evaluation floor is separated from the unverified 449 nanosecond electrical claim

The P0 suite contains 11 tests covering the ten recorded repair findings.

### 4.2 Chronicle provenance

Primary artifacts:

- `chronicle/chronicle.py`
- `chronicle/test_chronicle.py`
- `chronicle/__init__.py`

Chronicle provides:

- append-only JSONL persistence
- SHA-256 hash chaining
- chain verification
- ledger head
- Merkle root
- external head-anchor helpers

Canonical claim: **tamper-evident, not tamper-proof**.

A full attacker-controlled rewrite remains detectable only when the head or Merkle root is anchored outside the attacker-controlled store.

### 4.3 Layer 0 source policy

Primary artifacts:

- `src/bootstrap_policy.py`
- `tests/test_bootstrap.py`
- `LAYER0_SOURCE_POLICY.md`

The policy rejects obvious binary, packaged, precompiled, or opaque repository inputs using declared filename, suffix, NUL-byte, and magic-signature rules.

It does not establish:

- a GNU Mes-style bootstrap
- compiler or interpreter provenance
- reproducible toolchain construction
- diverse double compilation
- elimination of the Trusting Trust problem

### 4.4 Weaver Recognition Kernel

Primary artifacts:

- `src/recognition_kernel.py`
- `tests/test_recognition_kernel.py`
- `governance/LANGSEC_DOCTRINE.md`
- `governance/language_registry.json`

The registered language `CATHEDRAL-GOVERNANCE-REQUEST-v1` enforces:

- strict UTF-8
- complete JSON recognition
- duplicate-field rejection
- unknown-field rejection
- trailing-data rejection
- NFC-normalized accepted strings
- total input, field, depth, object-count, and integer bounds
- exact Boolean and integer typing
- deterministic canonical serialization
- conversion into a typed `UnifiedRequest`
- no Chronicle, hardware, or execution effects before recognition succeeds

Current parser posture: **P3**.

P4 through P8 remain open: differential testing, fuzz/property testing, demonstrated resource bounds, endpoint-equivalence receipts, and independent reproduction.

### 4.5 Classifier Assurance Gate

Primary artifacts:

- `src/classifier_assurance.py`
- `tests/test_classifier_assurance.py`
- `governance/CLASSIFIER_ASSURANCE_DOCTRINE.md`
- `governance/VALIDATION_RECEIPT_004_CLASSIFIER_ASSURANCE.md`

Integrated invariants:

- `INV-AI-001`: Confidence Is Not Validity
- `INV-AI-002`: Distribution Shift Requires Abstention
- `INV-AI-003`: Independent Oracle Before Authority
- `INV-AI-004`: Optimization Resistance

The gate treats model outputs as proposals. Unknown or out-of-distribution claims, missing independent evidence, independent disagreement, and confidence-directed optimization all block authority eligibility.

An agreeing in-distribution check makes a claim eligible for later policy consideration only. It does not authorize execution.

### 4.6 Lucifer Latch RTL simulation

Primary artifacts:

- `hardware/lucifer_latch/lucifer_latch.v`
- `hardware/lucifer_latch/tb_lucifer_latch.v`
- `hardware/lucifer_latch/sim_results.log`
- `hardware/lucifer_latch/VERIFICATION_REPORT.md`

The simulation exercises reset, threshold behavior, the evaluation dwell, irreversible TRIGGERED state, and reset-only clearing.

Canonical evidence label: **RTL simulation PASS**.

This is not synthesis, place-and-route, timing closure, bitstream, silicon, or board-level verification.

---

## 5. Replay Status Correction

A generalized deterministic replay engine or workflow is **not implemented in this repository at the pinned commit**.

Chronicle provides persistent receipts, verification, ledger heads, Merkle roots, and anchoring helpers. Those are useful prerequisites for replay, but they are not equivalent to a complete replay engine.

Replay therefore remains a future milestone requiring:

- canonical event schemas
- deterministic state reconstruction
- version-pinned dependencies
- controlled time and randomness
- replay commands and fixtures
- divergence detection
- replay receipts
- independent reproduction

---

## 6. Reproduction Protocol

External reviewers should inspect and execute the repository rather than relying on this document.

```bash
git clone https://github.com/ryansctt1994-sudo/cathedral-verified.git
cd cathedral-verified
git checkout 8ab93420b6ce86c66834d697aabc6a672ba0ec73

# Requires Python 3 and Icarus Verilog.
make test
```

Equivalent focused commands:

```bash
PYTHONPATH=src:. python3 -m unittest tests.test_bootstrap -v
PYTHONPATH=src:. python3 -m unittest tests.test_recognition_kernel -v
PYTHONPATH=src:. python3 -m unittest tests.test_classifier_assurance -v
cd chronicle && python3 test_chronicle.py && cd ..
PYTHONPATH=src:. python3 -m unittest discover -s tests -p 'test_p0_regressions.py' -v
make test-hw
```

Reviewers should record:

- operating system
- Python version
- Icarus Verilog version
- exact commit
- command transcript
- pass/fail output
- deviations from CI
- hashes of any exported receipts

A successful run outside the repository-controlled CI environment is the next evidence milestone.

---

## 7. Verified CI Receipt

Pinned validated implementation commit:

`8ab93420b6ce86c66834d697aabc6a672ba0ec73`

GitHub Actions run #47 passed:

- Layer 0 source-policy checks
- Weaver Recognition Kernel checks
- Classifier Assurance checks
- Chronicle verification suite
- Cathedral Forge P0 regression suite
- Lucifer Latch RTL simulation

This is repository-controlled CI evidence. It is not independent external reproduction.

---

## 8. Explicit Non-Claims and Future Work

The repository does not currently establish:

- production readiness
- operational deployment
- independent verification
- physical FPGA validation
- synthesis or timing closure
- authenticated real hardware transport
- external WORM-backed Chronicle anchoring
- a generalized replay engine
- full source bootstrapping or compiler provenance
- regulatory or compliance certification
- universal out-of-distribution detection
- domain-specific medical, legal, defense, or autonomous-system validation
- AGI or ASI capability or authority

All such claims remain withheld.

---

## 9. Evidence Philosophy

Promotion is evidence-driven and artifact-scoped.

- architecture does not imply implementation
- implementation does not imply verification
- passing tests do not imply exhaustive correctness
- passing CI does not imply independent reproduction
- RTL simulation does not imply hardware validation
- a confidence score does not imply truth
- a receipt does not imply an external anchor
- a prototype does not imply deployment
- documentation does not imply correctness

Negative findings are valid evidence and should become tracked gaps rather than being hidden or rhetorically softened.

---

## 10. Architectural Position

```text
Model or external input
        ↓
Recognition and source-policy gates
        ↓
Classifier assurance and semantic policy
        ↓
Typed governance runtime
        ↓
Hardware-readback boundary or fail-closed substitute
        ↓
Chronicle receipt and evidence state
        ↓
Future replay and evidence promotion
```

Cathedral Forge is intended to complement models and orchestration systems by constraining authority, preserving provenance, and making unsupported promotion harder.

---

## 11. Current Differentiators

The strongest supported differentiators are:

- explicit claim and evidence boundaries
- fail-closed hardware and authority semantics
- canonical LANGSEC recognition before effects
- raw model confidence stripped of authority
- complete Chronicle receipt integration
- adversarial and mutation-oriented regression tests
- repository/CI-pinned review package
- hardware-adjacent safety exploration with simulation clearly separated from physical verification

These differentiators remain meaningful only while they remain reproducible and accurately scoped.

---

## 12. Remaining Milestones

Highest-priority next steps:

1. Independent reproduction of the pinned commit.
2. Publication of raw external transcripts and environment metadata.
3. Public issue-driven review and defect tracking.
4. Immutable tagged release after independent reproduction.
5. Generalized deterministic replay implementation and receipts.
6. External Chronicle anchoring demonstration.
7. Parser P4 through P7 evidence.
8. FPGA synthesis, place-and-route, timing closure, and board validation.
9. Real authenticated hardware transport.
10. Independent contributors and maintainers.

Further architecture documents should not substitute for these engineering gates.

---

## 13. Reviewer Checklist

Reviewers should confirm:

- repository and PR identity
- pinned commit
- branch distinction
- CI run and job results
- complete test commands
- Chronicle threat-model limits
- Recognition Kernel failure behavior
- classifier-confidence authority restrictions
- Layer 0 evidence boundary
- RTL simulation scope
- documentation-to-code consistency
- explicit non-claims

Any deviation should be documented publicly with command output and exact artifact references.

---

## 14. Canonical Status

```text
PROJECT: ZOREL-717 / Cathedral Forge
REPOSITORY: ryansctt1994-sudo/cathedral-verified
REVIEW TARGET: PR #1
PINNED IMPLEMENTATION: 8ab93420b6ce86c66834d697aabc6a672ba0ec73

SYSTEM POSTURE: Integrated prototype
EVIDENCE: E2 repository/CI candidate
RECOGNITION ASSURANCE: P3
INDEPENDENT REPRODUCTION: PENDING
HARDWARE: RTL SIMULATION ONLY
GENERAL REPLAY ENGINE: NOT IMPLEMENTED
PRODUCTION AUTHORITY: NONE / HOLD
```

---

## 15. Closing Statement

Cathedral Forge is presented as an engineering prototype for AI runtime governance. Its current contribution is not a claim of superior intelligence. It is a concrete attempt to bind inputs, model outputs, policy decisions, provenance, and hardware-adjacent safety signals to explicit evidence and fail-closed authority rules.

The next meaningful milestone is independent reproduction of the pinned implementation commit. Until that occurs, all higher-level claims remain intentionally withheld under the project's own governing principle:

> Evidence governs promotion.
