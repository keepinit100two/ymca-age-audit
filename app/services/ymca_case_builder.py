from app.domain.ymca_schemas import (
    YmcaEvaluationResult,
    MemberCase,
    MemberCaseIdentity,
    MemberCaseQualification,
    MemberCaseControl,
    CaseCreationDecision,
)


class YmcaCaseBuilder:
    def build_case_decision(self, result: YmcaEvaluationResult) -> CaseCreationDecision:
        if result.decision not in {"ELIGIBLE", "NEEDS_ENRICHMENT"}:
            return CaseCreationDecision(
                should_create_case=False,
                reason="RESULT_NOT_CASE_WORTHY",
                case=None,
            )

        if result.transition_type is None:
            return CaseCreationDecision(
                should_create_case=False,
                reason="NO_TRANSITION_TYPE",
                case=None,
            )

        effective_period = self._derive_effective_period(result.transition_type)
        case_semantic_key = self._build_case_semantic_key(
            member_id=result.member_id,
            membership_id=result.membership_id,
            transition_type=result.transition_type,
            effective_period=effective_period,
        )
        case_id = self._build_case_id(case_semantic_key)

        case = MemberCase(
            identity=MemberCaseIdentity(
                case_id=case_id,
                case_semantic_key=case_semantic_key,
                member_id=result.member_id,
                membership_id=result.membership_id,
                branch_id=result.branch_id,
            ),
            qualification=MemberCaseQualification(
                transition_type=result.transition_type,
                target_membership_type=result.target_membership_type,
                decision=result.decision,
                exclusion_codes=result.exclusion_codes,
                enrichment_required=result.enrichment_required,
                in_scope=result.in_scope,
                out_of_scope_reason=result.out_of_scope_reason,
            ),
            control=MemberCaseControl(
                effective_period=effective_period,
                version=1,
            ),
        )

        return CaseCreationDecision(
            should_create_case=True,
            reason="CASE_CREATED_FROM_EVALUATION_RESULT",
            case=case,
        )

    def _derive_effective_period(self, transition_type: str) -> str:
        """
        Placeholder production contract:
        later this should be derived from real event timing / birthday month.
        For now it gives us a stable contract surface.
        """
        return transition_type

    def _build_case_semantic_key(
        self,
        *,
        member_id: str,
        membership_id: str,
        transition_type: str,
        effective_period: str,
    ) -> str:
        return f"{member_id}:{membership_id}:{transition_type}:{effective_period}"

    def _build_case_id(self, case_semantic_key: str) -> str:
        return f"case::{case_semantic_key}"