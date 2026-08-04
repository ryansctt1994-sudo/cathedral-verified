# Canonical LANGSEC Doctrine

## Governing Principle

> Untrusted input is a proposed computation, not passive data. It must be fully recognized, bounded, canonically interpreted, and stripped of raw authority before it can affect execution or state.

This doctrine applies to Weaver, Forge, Cathedral, and every attached subsystem.

## Canonical Recognition Flow

```text
Untrusted bytes or text
        ↓
Size and resource bounds
        ↓
Formal recognition
        ↓
Canonicalization
        ↓
Typed representation
        ↓
Semantic validation
        ↓
Authorization
        ↓
Execution or state mutation
```

Nothing may jump directly from a raw string, document, serialized object, model output, or byte stream into an authority-bearing action.

## Invariants

### INV-LANGSEC-001: Full Recognition

No untrusted input may influence execution, authority, evidence status, promotion, or persistent state until the complete declared structure has been recognized.

### INV-LANGSEC-002: Single Canonical Meaning

Every accepted input must produce exactly one canonical interpretation. Ambiguous, duplicate, contradictory, differently normalizable, or multiply interpretable inputs must be rejected.

### INV-LANGSEC-003: Parse Before Effects

Parsing and semantic validation must finish before file writes, network requests, credential use, subprocess execution, database mutation, or authority delegation.

### INV-LANGSEC-004: No Raw-Input Authority

Raw prompts, strings, documents, serialized objects, and model outputs cannot directly carry executable authority. Authority may exist only in typed, validated capability objects.

### INV-LANGSEC-005: Least Expressive Language

Every protocol, configuration format, and command schema must use the weakest language sufficient for its purpose:

```text
fixed schema
→ regular grammar
→ deterministic context-free grammar
→ restricted expression language
→ general-purpose language only when unavoidable
```

Anything more expressive is an explicit execution environment requiring isolation, resource limits, and a higher evidence burden.

### INV-LANGSEC-006: Bounded Recognition

Every input boundary must enforce limits on total length, field length, nesting depth, expansion ratio, recursion, processing time, memory use, object count, and output size where applicable.

### INV-LANGSEC-007: Endpoint Semantic Equivalence

Sender, verifier, proxy, runtime, and archive must agree on grammar, normalization, duplicate-field handling, encoding, ordering, defaults, errors, and canonical serialization.

## Shotgun Parsing Prohibition

> Input interpretation must not be scattered across business logic.

Prohibited pattern:

```text
split string
→ inspect one field
→ pass raw remainder
→ reinterpret later
→ sanitize again
→ execute
```

Required pattern:

```text
raw_request: bytes
→ validated_request: GovernanceRequest
→ authorized_action: CapabilityBoundAction
```

Each accepted input language must have one authoritative parser and one canonical serializer recorded in `governance/language_registry.json`.

## Parser Evidence Ladder

The parser ladder is orthogonal to the system evidence ladder.

| Level | Recognition assurance |
|---|---|
| P0 | Input format informally described |
| P1 | Grammar and bounds documented |
| P2 | Canonical parser implemented |
| P3 | Negative and malformed-input tests pass |
| P4 | Differential parser testing passes |
| P5 | Property-based and fuzz testing passes |
| P6 | Resource-exhaustion bounds demonstrated |
| P7 | Endpoint-equivalence evidence produced |
| P8 | Independent reproduction completed |

## Model Output Rule

Model-generated text is a proposal only. JSON-shaped prose, Python, YAML, SQL, shell fragments, governance commands, or tool-call-like text carry no authority until recognized into a declared schema, semantically validated, capability checked, and authorized.

## Weird-Machine Review

Every authority-bearing parser review must ask:

1. What unintended states can malformed inputs reach?
2. Can error recovery become programmable?
3. Can parser disagreement create a second interpretation?
4. Can resource exhaustion become a control channel?
5. Can partial parsing cause partial effects?
6. Can invalid fragments compose into valid execution?
7. Does deserialization instantiate behavior rather than data?

## Current Implementation

`src/recognition_kernel.py` implements the first canonical Recognition Gate for `CATHEDRAL-GOVERNANCE-REQUEST-v1`.

It provides:

- strict UTF-8 recognition
- total input bounds
- duplicate-field rejection
- unknown-field rejection
- trailing-data rejection
- NFC enforcement
- nesting and object-count limits
- exact type and range validation
- deterministic canonical serialization
- typed conversion to `UnifiedRequest`
- a parser receipt containing the canonical SHA-256
- a raw-input execution entrypoint that completes recognition before invoking Cathedral Forge

Current parser posture: **P3 candidate**, subject to the current branch CI result.

## Governing Law

> No recognition, no interpretation. No canonical interpretation, no authority. No bounded authority, no execution.
