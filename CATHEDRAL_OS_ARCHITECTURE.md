# Cathedral-OS Architecture Baseline
**Version:** 0.1.1-draft  
**Status:** Architecture Locked — Ready for Genesis Commit  
**Date:** 2026-07-25  
**Authority:** Consolidated from pruned_core_integration_map, Angela specifications, and T81 analysis documents.  
**Amendment 0.1.1:** Injected mandatory local measurement proxies (embedding-drift, token-entropy) and elevated Observer isolation + local-measurement rules to constitutional invariants (§6.1, §8).

---

## 1. Purpose and Scope

This document establishes the definitive architectural baseline for integrating the deterministic T81 kernel with the Angela safety architecture into the Cathedral-OS substrate. It resolves the structural gap between theoretical specifications held in Google Drive and the executable repositories (`zorel-kernel`, `cathedral-verified`).

The architecture enforces a strict separation between:

- **Deterministic core** (T81 state representation + Angela L1–L4 enforcement layers)
- **Probabilistic external systems** (Ruflo, OpenMythos, or any multi-agent cognitive layer)

No external probabilistic system may mutate CanonicalState or bypass the Angela L1 hardware latch.

---

## 2. Core Theses (Angela)

1. System stability under increasing complexity is achieved through structural constraint and enforced boundaries, not training, intent modeling, or internal interpretability.
2. Safety must be a property of system structure (hardware, timing, mathematics), not of model behavior or human vigilance.

Alignment is enforced externally and temporally, not internally or cognitively.

---

## 3. Four-Layer Safety Architecture (Angela)

| Layer | Name | Function | Implementation Status |
|-------|------|----------|-----------------------|
| **L1** | Hardware | Physical interrupt and irreversible reset via FPGA latch. Sub-millisecond hard-stop independent of software or AI state. | Specified (Verilog + FPGA bitstream) |
| **L2** | Temporal | Compliance hysteresis FSM with 300-second clean-window lockout + Merkle-based state integrity. Prevents flapping and oscillatory failure. | Specified (deterministic FSM) |
| **L3** | Semantic | Policy-enforced intent authorization and audit logging prior to execution (ACE v4.2 DAG-based plan parsing). | Specified |
| **L4** | Justice | Deterministic, bias-auditable allocation and penalty logic using fixed-point integer arithmetic. | Specified |

**Execution Sequence (non-negotiable):**  
`Observe → Authorize → Allocate → Commit`

All inter-layer signal contracts are frozen by the **Unified Handshake Protocol** to eliminate race conditions and undefined behavior.

---

## 4. T81 Deterministic Kernel

T81 provides the governed logical machine substrate:

- Determinism and full replayability of every state transition
- Formal proofs of state transitions
- Explicit policy enforcement (Axion)
- Ternary-native arithmetic (`T81Fraction` exact rational arithmetic)
- Auditable self-modification under policy (Tier 4 reflection)

**CanonicalState** is the sole mutable state representation. Deterministic hashing of CanonicalState enables the governance-memory causal-link model.

T81 is treated as infrastructure (brainstem/spinal cord). Any neural or multi-agent cognitive capability is treated as a supervised cortex that may never write directly to CanonicalState.

---

## 5. Component Integration Map (P1–P3)

Source: `pruned_core_integration_map`

### Priority 1 (Immediate)

| Source Artifact | Target | Mapping |
|-----------------|--------|---------|
| `runtime_gate.py` | `dual_track_detection.py` (stub 1) | GateMode enum: `EXECUTE` / `THROTTLE` / `BLOCK` / `HARD_FAIL`. Maps directly to 3-tier alerting. `p_fail` feeds EWMA anomaly baseline. Closes open stub 1. |
| `chronicle.py` | GOVERNANCE_MEMORY.jsonl + SWD | WORM append + SHA-256 chaining. Chronicle becomes the hardware-layer forensic sink. Requires schema adapter for causal/supersession fields. |

### Priority 2

| Source Artifact | Target | Mapping |
|-----------------|--------|---------|
| `constraint_engine.py` | Adjudicator pre-check | Z3 SMT validation of position/energy bounds before AEGIS policy evaluation. |
| `state.py` | T81 ternary kernel | CanonicalState + T81Fraction. Deterministic hashing for governance memory. |
| `delta.py` | `decision_lattice.py` | NullDelta → PAUSE semantics; ViabilityDelta → Safety × Temporal × Causal product lattice. |
| `observer.py` | dual_track stub 2 | EKF state estimation (see §6 Isolation Rules). |
| `queue.py` + `latency.py` | dual_track stub 3 | Bounded queue dynamics + p95 latency. Closes remaining dual_track stubs. |

### Priority 3

| Source Artifact | Target | Mapping |
|-----------------|--------|---------|
| `p_fail_trainer.py` | Quillan persona tier selection | Logistic regression on (θ, θ̇, x, ẋ, queue, latency, control_history) → effort routing. |
| Test / demo artifacts | Existing ~1776-test suite | cartpole_with_gate, Monte-Carlo runner, adversarial unfair tests. |

---

## 6. Observer Isolation Rules (Mandatory)

All Sentinel-class modules and `observer.py` (dual_track stub 2) are **strictly passive, read-only observer components**.

- Zero state-mutation rights within the EKF state-estimation track.
- May emit observations and anomaly scores only.
- May never issue GateMode commands, write to CanonicalState, or trigger L1 latch.
- Any write attempt is a hard architectural violation and must result in `HARD_FAIL`.

### 6.1 Monitoring Measurement Mandate

The theoretical statistical monitoring model **must** substitute wide-horizon trajectory-space metrics with discrete, local, empirically computable proxies:

- **Local embedding-drift** — measured on the current token or state embedding relative to a fixed, versioned reference embedding.
- **Token-entropy** — computed over a bounded local window only (no multi-step future trajectory expansion).

Wide-horizon, non-computable mathematical notation is prohibited in the monitoring path. All Sentinel outputs that feed the dual-track alerting tiers or EWMA baseline must be derived exclusively from these discrete local instruments. This constraint ensures empirical buildability and prevents the introduction of non-executable theoretical constructs into the runtime path.

This rule preserves deterministic safety guarantees under all operating conditions.

---

## 7. Probabilistic Boundary Definition

External multi-agent or probabilistic systems (Ruflo, OpenMythos, any LLM-based cognitive layer) may interact with Cathedral-OS **only** through the Unified Handshake Protocol.

### Allowed Interface Surface

1. Read-only observation streams (telemetry, Chronicle digests, GateMode status).
2. Authorization requests that enter the L3 Semantic layer for policy evaluation.
3. Allocation requests that enter the L4 Justice layer (fixed-point, deterministic).

### Forbidden Actions

- Direct mutation of CanonicalState.
- Bypass of the Angela L1 hardware latch.
- Injection of non-deterministic control signals into the T81 kernel.
- Any write that would violate the fail-closed invariant: `¬constraint_ok ⇒ HARD_FAIL`.

The Unified Handshake Protocol freezes inter-layer contracts. Any attempt to circumvent the handshake is treated as an adversarial input and triggers L1 latch.

---

## 8. Retained Invariants (Constitutional Layer)

The following invariants are carried forward and are non-negotiable:

1. **Fail-closed:** `¬constraint_ok ⇒ HARD_FAIL`
2. **Bounded queue:** `q ≤ max_queue`
3. **Position & energy bounds:** Z3-validated
4. **p_fail monotonicity:** `p_fail` is monotonic in queue depth and latency
5. **Observer isolation:** Sentinel-class modules possess strictly zero state-mutation rights
6. **Local measurement only:** Monitoring instrumentation is restricted to discrete local embedding-drift and token-entropy proxies; wide-horizon trajectory-space metrics are forbidden

Dropped (correctly) until derived or validated:

- Betti-1 ≤ 0.045
- Goldschmidt limit
- Entropy cap
- Trillion limits

These remain consistent with the existing 25 pinned invariants of the Cathedral constitutional layer.

---

## 9. Genesis Block and Change Control

- **Genesis Block:** Signed manifest binding hardware bitstreams, FSM logic, policy rules, and fixed-point coefficients into a single cryptographic root.
- **Bootloader/FPGA Verifier:** System will not boot unless all hashes and signatures match the Tier-1 certified state.
- **Change Control:** Any modification (including coefficient updates) requires full re-certification and deterministic replay.
- **Gatekeeper:** `gatekeeper_pqc.py` enforces human authorization using ML-DSA (Dilithium-5). Four distinct human roles must cryptographically approve any change request before CI/CD is unlocked.

---

## 10. Implementation Sequence (Locked)

1. **Architecture baseline** (this document) — complete.
2. **P1 stubs:** Translate `runtime_gate.py` (GateMode) and `chronicle.py` (WORM + SHA-256) into pull requests against `cathedral-verified` / `zorel-kernel`.
3. **Observer isolation enforcement:** Implement read-only contracts for all Sentinel-class modules.
4. **L1 latch verification model:** Produce RTL or simulation harness for the Hardware-Enforced Irreversible Latch.
5. **Boundary interface:** Expose only the Unified Handshake Protocol surface to any external probabilistic system.
6. **External validation:** Independent FPGA timing review with fault injection; external red-team evaluation; publication of schematics, timing data, hashes, and test vectors without narrative framing.

---

## 11. Maturity Snapshot

| Dimension | Assessment |
|-----------|------------|
| Theory | ~95 % complete and internally coherent |
| Implementation | ~70 % real and buildable |
| External validation | ~5 % (hostile review and independent testing outstanding) |

---

## 12. Document Control

- This file is the single source of truth for architectural decisions.
- All subsequent pull requests must reference section numbers herein.
- Amendments require the same change-control process defined in §9.

**End of Architecture Baseline**
