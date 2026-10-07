import unittest

from classifier_assurance import (
    AssuranceDisposition,
    DistributionStatus,
    IndependentCheck,
    ModelClaim,
    assess_model_claim,
    run_confidence_directed_search,
)


class ClassifierAssuranceTests(unittest.TestCase):
    def test_high_confidence_does_not_create_authority(self):
        claim = ModelClaim(
            model_id="demo-model",
            label="replicator",
            confidence=0.9999,
            distribution_status=DistributionStatus.UNKNOWN,
        )

        verdict = assess_model_claim(claim)

        self.assertFalse(verdict.authority_eligible)
        self.assertEqual(verdict.disposition, AssuranceDisposition.REJECT_AUTHORITY)
        self.assertIn("distribution_status:unknown", verdict.reasons)
        self.assertIn("independent_ground_truth_check_missing", verdict.reasons)

    def test_out_of_distribution_claim_fails_closed_even_with_high_confidence(self):
        claim = ModelClaim(
            model_id="demo-model",
            label="positive",
            confidence=1.0,
            distribution_status=DistributionStatus.OUT_OF_DISTRIBUTION,
        )
        check = IndependentCheck("oracle", agrees=True, evidence_ref="receipt-1")

        verdict = assess_model_claim(claim, [check])

        self.assertFalse(verdict.authority_eligible)
        self.assertIn("distribution_status:out_of_distribution", verdict.reasons)

    def test_independent_disagreement_overrides_model_confidence(self):
        claim = ModelClaim(
            model_id="demo-model",
            label="positive",
            confidence=0.999,
            distribution_status=DistributionStatus.IN_DISTRIBUTION,
        )
        check = IndependentCheck("oracle", agrees=False, evidence_ref="receipt-2")

        verdict = assess_model_claim(claim, [check])

        self.assertFalse(verdict.authority_eligible)
        self.assertIn("independent_check_disagrees", verdict.reasons)

    def test_confidence_optimized_claim_is_adversarial_evidence(self):
        claim = ModelClaim(
            model_id="demo-model",
            label="positive",
            confidence=0.999,
            distribution_status=DistributionStatus.IN_DISTRIBUTION,
            confidence_was_optimization_target=True,
        )
        check = IndependentCheck("oracle", agrees=True, evidence_ref="receipt-3")

        verdict = assess_model_claim(claim, [check])

        self.assertFalse(verdict.authority_eligible)
        self.assertIn("confidence_directed_optimization_detected", verdict.reasons)

    def test_agreed_in_distribution_claim_is_only_eligible_for_consideration(self):
        claim = ModelClaim(
            model_id="demo-model",
            label="positive",
            confidence=0.8,
            distribution_status=DistributionStatus.IN_DISTRIBUTION,
        )
        check = IndependentCheck("oracle", agrees=True, evidence_ref="receipt-4")

        verdict = assess_model_claim(claim, [check])

        self.assertTrue(verdict.authority_eligible)
        self.assertEqual(verdict.disposition, AssuranceDisposition.CONSIDER)
        self.assertNotEqual(verdict.disposition.value, "authorize")

    def test_confidence_directed_search_finds_high_confidence_false_positive(self):
        alphabet = "abc"

        def mutate(value: str):
            for index in range(len(value)):
                for symbol in alphabet:
                    if symbol != value[index]:
                        yield value[:index] + symbol + value[index + 1 :]

        def score(value: str) -> float:
            return value.count("a") / len(value)

        def oracle(value: str) -> bool:
            return value == "abc"

        receipt = run_confidence_directed_search(
            start="ccc",
            mutate=mutate,
            score=score,
            oracle=oracle,
            query_budget=30,
            false_positive_threshold=0.99,
        )

        self.assertTrue(receipt.false_positive_found)
        self.assertEqual(receipt.best_candidate, "aaa")
        self.assertEqual(receipt.best_confidence, 1.0)
        self.assertFalse(oracle(receipt.best_candidate))

    def test_search_validates_score_bounds(self):
        with self.assertRaises(ValueError):
            run_confidence_directed_search(
                start="x",
                mutate=lambda value: [value],
                score=lambda value: 2.0,
                oracle=lambda value: False,
                query_budget=1,
            )


if __name__ == "__main__":
    unittest.main()
