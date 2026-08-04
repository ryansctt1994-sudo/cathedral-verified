# Validation Receipt 004: Classifier Assurance and Confidence-Directed Spoofing

**Date:** 2026-07-10  
**Project:** ZOREL-717 / Cathedral Forge  
**Source study:** Ankit Gupta and Christoph Adami, *Can AI Detect Life? Lessons from Artificial Life*  
**Primary source:** https://arxiv.org/abs/2604.11915  
**Institutional summary:** https://eeb.msu.edu/news/its-disturbingly-easy-to-trick-ai-into-seeing-aliens.aspx

## Validation Finding

The social-media post is directionally accurate, with two corrections:

1. The paper reports **99.97% accuracy** for the focal multi-layer perceptron on a balanced sampled test split.
2. The attack reached **100% mean spoofing confidence by 150 model queries** in the focal greedy-search experiments. This is not identical to saying that exactly 150 source-code edits were always required.

The study used Avida length-9 digital organisms. A greedy hill climber proposed single-site mutations and retained mutations that increased the classifier's predicted probability of self-replication. The resulting high-confidence endpoints were checked against the known Avida replicator set and were false positives.

## Scope Boundary

The study demonstrates a severe failure mode in a controlled artificial-life classification domain:

- near-perfect sampled test accuracy
- high-confidence false positives under targeted search
- vulnerability across multiple model classes and search procedures
- classifier confidence functioning poorly as an optimization oracle

It does **not** directly prove equivalent failure rates in healthcare, autonomous vehicles, security systems, or physical astrobiology instruments. Those are plausible risk analogies requiring domain-specific validation.

## Canonical Engineering Lesson

> A model may be an excellent discriminator on sampled in-distribution data while remaining an unsafe oracle over a wider or adversarially searched input space.

Therefore:

- accuracy is not authority
- confidence is not validity
- unknown distribution status requires abstention
- confidence-directed optimization is an adversarial condition
- independent ground truth must precede authority eligibility
- classifier results remain proposals until separate policy and capability authorization

## Integrated Artifacts

- `governance/CLASSIFIER_ASSURANCE_DOCTRINE.md`
- `src/classifier_assurance.py`
- `tests/test_classifier_assurance.py`
- `Makefile` target: `test-classifier-assurance`
- GitHub Actions step: `Run classifier assurance checks`

## Integrated Invariants

- `INV-AI-001`: Confidence Is Not Validity
- `INV-AI-002`: Distribution Shift Requires Abstention
- `INV-AI-003`: Independent Oracle Before Authority
- `INV-AI-004`: Optimization Resistance

## Implemented Behaviors

- high confidence without independent evidence is rejected for authority
- unknown or out-of-distribution claims fail closed
- independent disagreement overrides confidence
- confidence-directed optimization marks a claim as adversarial evidence
- independent agreement yields consideration eligibility only, never direct authorization
- a generic greedy mutation harness emits a spoof-search receipt
- a regression fixture demonstrates a 100% confidence false positive against an independent oracle

## CI Receipt

```text
Validated head: 18d14ba9a2f22295979935413bcb5bb087d3bb4b
GitHub Actions run: #45
Layer 0 source-policy checks: PASS
Weaver Recognition Kernel checks: PASS
Classifier assurance checks: PASS
Chronicle verification suite: PASS
Cathedral Forge P0 regressions: PASS
Lucifer Latch RTL simulation: PASS
Overall workflow: SUCCESS
```

## Evidence Posture

```text
Classifier assurance scaffold: repository/CI verified
Universal OOD detection: NOT CLAIMED
Domain calibration: NOT ESTABLISHED
External reproduction: REQUIRED
Production authority: NONE / HOLD
```
