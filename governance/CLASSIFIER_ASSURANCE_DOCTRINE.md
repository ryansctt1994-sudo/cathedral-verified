# Classifier Assurance Doctrine

## Governing Principle

> Accuracy measures performance on a sampled distribution. Confidence measures a model's internal score. Neither is proof that a claim is true, in distribution, or safe to act upon.

This doctrine applies to Weaver, Forge, Cathedral, and attached systems whenever a statistical model, neural network, heuristic classifier, anomaly detector, or model-generated score influences evidence, promotion, execution, or persistent state.

## Canonical Invariants

### INV-AI-001: Confidence Is Not Validity

A confidence score, probability, ranking, or held-out accuracy may not independently authorize execution, evidence promotion, or state mutation.

### INV-AI-002: Distribution Shift Requires Abstention

Unknown or out-of-distribution inputs must fail closed for authority-bearing use unless an independently validated procedure covers that distribution.

### INV-AI-003: Independent Oracle Before Authority

A model claim must be checked by a ground-truth-capable and independently specified method before it can become eligible for authority consideration.

An agreeing check makes the claim eligible for later policy evaluation. It does not itself authorize action.

### INV-AI-004: Optimization Resistance

Any input found by optimizing, searching, hill-climbing, mutating, or otherwise selecting against the model's own confidence is adversarial evidence. High confidence under such a process is grounds for rejection, not promotion.

## Canonical Flow

```text
Model output
    ↓
Typed ModelClaim
    ↓
Distribution status
    ↓
Independent ground-truth check
    ↓
Confidence-directed mutation challenge
    ↓
Classifier Assurance Verdict
    ↓
Separate policy and capability authorization
```

## Required Validation

Authority-relevant classifiers should maintain receipts for:

- dataset and sampling assumptions
- class balance and base rates
- held-out performance
- calibration
- known distribution boundaries
- out-of-distribution tests
- confidence-directed search
- mutation and metamorphic tests
- independently computed ground truth
- false-positive and false-negative costs
- abstention behavior
- endpoint/version identity

## Prohibited Claims

The following conclusions may not be drawn from accuracy or confidence alone:

- the model has solved the task
- the output is verified
- the sample is in distribution
- a high-confidence result is safe to execute
- no adversarial basin exists
- performance generalizes to a larger combinatorial domain

## Study Integration Receipt

The motivating study, *Can AI Detect Life? Lessons from Artificial Life* by Ankit Gupta and Christoph Adami, reported a classifier with 99.97% accuracy on a balanced sampled test split. A greedy confidence-directed search nevertheless found non-replicating sequences assigned 100% replicator confidence in all focal runs by 150 model queries.

The engineering lesson integrated here is narrow and durable:

> A discriminative model may perform nearly perfectly on sampled test data while remaining an unsafe optimization oracle over the wider input space.

This does not establish that every classifier fails identically, nor does it directly validate claims about healthcare, autonomous vehicles, or physical astrobiology systems. Those require domain-specific evidence.

## Current Implementation

`src/classifier_assurance.py` provides:

- typed `ModelClaim`
- explicit distribution status
- independent-check receipts
- a fail-closed classifier assurance verdict
- a generic confidence-directed mutation search
- negative evidence when high-confidence false positives are discovered

`tests/test_classifier_assurance.py` demonstrates that:

- high confidence without independent evidence carries no authority
- unknown and out-of-distribution inputs fail closed
- independent disagreement overrides confidence
- confidence-directed optimization is treated as adversarial evidence
- an agreeing in-distribution check yields consideration eligibility, not authorization
- a toy classifier can be driven to a 100% confidence false positive

## Evidence Boundary

This module is an assurance scaffold. It does not implement a universal out-of-distribution detector, prove calibration, or replace domain ground truth. Production authority remains NONE / HOLD.
