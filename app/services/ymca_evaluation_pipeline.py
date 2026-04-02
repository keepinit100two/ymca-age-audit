from app.domain.ymca_schemas import DaxkoRawRow, YmcaEvaluationResult
from app.services.ymca_normalizer import YmcaNormalizationService
from app.services.ymca_transition_classifier import YmcaTransitionClassifier
from app.services.ymca_eligibility_evaluator import YmcaEligibilityEvaluator


class YmcaEvaluationPipeline:
    def __init__(
        self,
        normalizer: YmcaNormalizationService | None = None,
        classifier: YmcaTransitionClassifier | None = None,
        evaluator: YmcaEligibilityEvaluator | None = None,
    ):
        self.normalizer = normalizer or YmcaNormalizationService()
        self.classifier = classifier or YmcaTransitionClassifier()
        self.evaluator = evaluator or YmcaEligibilityEvaluator()

    def run(self, raw: DaxkoRawRow) -> YmcaEvaluationResult:
        member, membership, snapshot, flags = self.normalizer.normalize(raw)
        transition = self.classifier.classify(membership, snapshot, flags)
        eligibility = self.evaluator.evaluate(
            member,
            membership,
            snapshot,
            flags,
            transition,
        )

        return YmcaEvaluationResult(
            member_id=member.member_id,
            membership_id=membership.membership_id,
            branch_id=member.branch_id,
            transition_type=transition.transition_type,
            target_membership_type=transition.target_membership_type,
            decision=eligibility["decision"],
            exclusion_codes=eligibility["exclusion_codes"],
            enrichment_required=eligibility["enrichment_required"],
            in_scope=transition.in_scope,
            out_of_scope_reason=transition.out_of_scope_reason,
        )