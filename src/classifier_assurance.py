"""Classifier assurance for evidence-governed systems.

High held-out accuracy and high confidence are measurements, not authority.
This module treats every model output as a proposal that must survive
distribution checks, independent verification, and confidence-directed
mutation challenges before it can influence evidence promotion or action.

The module is intentionally model-agnostic. It does not claim to solve
out-of-distribution detection. Instead, unknown distribution status fails
closed for authority-bearing use.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Generic, Iterable, TypeVar


INV_AI_001 = "INV-AI-001"  # Confidence is not validity.
INV_AI_002 = "INV-AI-002"  # Unknown/OOD inputs cannot carry authority.
INV_AI_003 = "INV-AI-003"  # Independent verification precedes authority.
INV_AI_004 = "INV-AI-004"  # Confidence-directed optimization is adversarial evidence.


class DistributionStatus(str, Enum):
    IN_DISTRIBUTION = "in_distribution"
    UNKNOWN = "unknown"
    OUT_OF_DISTRIBUTION = "out_of_distribution"


class AssuranceDisposition(str, Enum):
    CONSIDER = "consider"
    REQUIRE_REVIEW = "require_review"
    REJECT_AUTHORITY = "reject_authority"


@dataclass(frozen=True)
class ModelClaim:
    model_id: str
    label: str
    confidence: float
    distribution_status: DistributionStatus = DistributionStatus.UNKNOWN
    confidence_was_optimization_target: bool = False


@dataclass(frozen=True)
class IndependentCheck:
    checker_id: str
    agrees: bool
    evidence_ref: str
    ground_truth_capable: bool = True


@dataclass(frozen=True)
class AssuranceVerdict:
    disposition: AssuranceDisposition
    authority_eligible: bool
    reasons: tuple[str, ...]
    invariants: tuple[str, ...]


def assess_model_claim(
    claim: ModelClaim,
    checks: Iterable[IndependentCheck] = (),
) -> AssuranceVerdict:
    """Assess whether a model claim may enter policy consideration.

    `authority_eligible` means only that the claim cleared this narrow gate.
    It does not itself authorize execution, promotion, or state mutation.
    """

    reasons: list[str] = []
    invariants: list[str] = [INV_AI_001]

    if not 0.0 <= claim.confidence <= 1.0:
        reasons.append("confidence_out_of_range")

    if claim.distribution_status is not DistributionStatus.IN_DISTRIBUTION:
        reasons.append(f"distribution_status:{claim.distribution_status.value}")
        invariants.append(INV_AI_002)

    checks_tuple = tuple(checks)
    capable_checks = tuple(check for check in checks_tuple if check.ground_truth_capable)
    if not capable_checks:
        reasons.append("independent_ground_truth_check_missing")
        invariants.append(INV_AI_003)
    elif any(not check.agrees for check in capable_checks):
        reasons.append("independent_check_disagrees")
        invariants.append(INV_AI_003)

    if claim.confidence_was_optimization_target:
        reasons.append("confidence_directed_optimization_detected")
        invariants.append(INV_AI_004)

    if reasons:
        return AssuranceVerdict(
            disposition=AssuranceDisposition.REJECT_AUTHORITY,
            authority_eligible=False,
            reasons=tuple(reasons),
            invariants=tuple(dict.fromkeys(invariants)),
        )

    return AssuranceVerdict(
        disposition=AssuranceDisposition.CONSIDER,
        authority_eligible=True,
        reasons=("independent_check_agrees", "distribution_declared_in_distribution"),
        invariants=(INV_AI_001, INV_AI_003),
    )


T = TypeVar("T")


@dataclass(frozen=True)
class SpoofSearchStep(Generic[T]):
    query: int
    candidate: T
    confidence: float
    oracle_positive: bool


@dataclass(frozen=True)
class SpoofSearchReceipt(Generic[T]):
    start: T
    best_candidate: T
    best_confidence: float
    query_count: int
    false_positive_found: bool
    threshold: float
    trajectory: tuple[SpoofSearchStep[T], ...]


def run_confidence_directed_search(
    *,
    start: T,
    mutate: Callable[[T], Iterable[T]],
    score: Callable[[T], float],
    oracle: Callable[[T], bool],
    query_budget: int,
    false_positive_threshold: float = 0.99,
) -> SpoofSearchReceipt[T]:
    """Greedy black-box search for a high-confidence false positive.

    The search is a validation tool. Finding a spoof is negative evidence
    against using the classifier confidence as an oracle.
    """

    if query_budget < 1:
        raise ValueError("query_budget must be positive")
    if not 0.0 <= false_positive_threshold <= 1.0:
        raise ValueError("false_positive_threshold must be within [0, 1]")

    current = start
    current_score = score(current)
    if not 0.0 <= current_score <= 1.0:
        raise ValueError("score must return values within [0, 1]")

    trajectory: list[SpoofSearchStep[T]] = [
        SpoofSearchStep(0, current, current_score, oracle(current))
    ]
    queries = 0

    while queries < query_budget:
        improved = False
        for candidate in mutate(current):
            if queries >= query_budget:
                break
            candidate_score = score(candidate)
            queries += 1
            if not 0.0 <= candidate_score <= 1.0:
                raise ValueError("score must return values within [0, 1]")
            if candidate_score > current_score:
                current = candidate
                current_score = candidate_score
                trajectory.append(
                    SpoofSearchStep(queries, current, current_score, oracle(current))
                )
                improved = True
                break
        if not improved:
            break

    false_positive = current_score >= false_positive_threshold and not oracle(current)
    return SpoofSearchReceipt(
        start=start,
        best_candidate=current,
        best_confidence=current_score,
        query_count=queries,
        false_positive_found=false_positive,
        threshold=false_positive_threshold,
        trajectory=tuple(trajectory),
    )
