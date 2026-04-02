from app.domain.ymca_schemas import YmcaEvaluationResult
from app.services.ymca_case_builder import YmcaCaseBuilder


def make_result(
    *,
    member_id="MEM-1",
    membership_id="M-1",
    branch_id="easton",
    transition_type="TEEN_TO_YOUNG_ADULT_19",
    target_membership_type="Young Adult",
    decision="ELIGIBLE",
    exclusion_codes=None,
    enrichment_required=None,
    in_scope=True,
    out_of_scope_reason=None,
):
    return YmcaEvaluationResult(
        member_id=member_id,
        membership_id=membership_id,
        branch_id=branch_id,
        transition_type=transition_type,
        target_membership_type=target_membership_type,
        decision=decision,
        exclusion_codes=exclusion_codes or [],
        enrichment_required=enrichment_required or [],
        in_scope=in_scope,
        out_of_scope_reason=out_of_scope_reason,
    )


def test_eligible_result_creates_case():
    result = make_result(decision="ELIGIBLE")
    decision = YmcaCaseBuilder().build_case_decision(result)

    assert decision.should_create_case is True
    assert decision.reason == "CASE_CREATED_FROM_EVALUATION_RESULT"
    assert decision.case is not None
    assert decision.case.identity.member_id == "MEM-1"
    assert decision.case.qualification.transition_type == "TEEN_TO_YOUNG_ADULT_19"


def test_needs_enrichment_result_creates_case():
    result = make_result(
        transition_type="FAMILY_DEPENDENT_AGE_OUT_28",
        target_membership_type=None,
        decision="NEEDS_ENRICHMENT",
        enrichment_required=["HOUSEHOLD_MEMBER_LOOKUP"],
    )
    decision = YmcaCaseBuilder().build_case_decision(result)

    assert decision.should_create_case is True
    assert decision.case is not None
    assert decision.case.qualification.decision == "NEEDS_ENRICHMENT"
    assert "HOUSEHOLD_MEMBER_LOOKUP" in decision.case.qualification.enrichment_required


def test_excluded_result_does_not_create_case():
    result = make_result(
        decision="EXCLUDED",
        exclusion_codes=["EXCLUDED_EMPLOYEE"],
    )
    decision = YmcaCaseBuilder().build_case_decision(result)

    assert decision.should_create_case is False
    assert decision.reason == "RESULT_NOT_CASE_WORTHY"
    assert decision.case is None


def test_out_of_scope_result_does_not_create_case():
    result = make_result(
        transition_type=None,
        target_membership_type=None,
        decision="EXCLUDED",
        exclusion_codes=["EXCLUDED_UNKNOWN"],
        in_scope=False,
        out_of_scope_reason="NO_SUPPORTED_TRANSITION_MATCH",
    )
    decision = YmcaCaseBuilder().build_case_decision(result)

    assert decision.should_create_case is False
    assert decision.reason == "RESULT_NOT_CASE_WORTHY"
    assert decision.case is None


def test_case_semantic_key_is_stable():
    result = make_result(
        member_id="MEM-42",
        membership_id="M-99",
        transition_type="ADULT_TO_ACTIVE_OLDER_ADULT_65",
        decision="ELIGIBLE",
    )
    decision = YmcaCaseBuilder().build_case_decision(result)

    assert decision.case is not None
    assert (
        decision.case.identity.case_semantic_key
        == "MEM-42:M-99:ADULT_TO_ACTIVE_OLDER_ADULT_65:ADULT_TO_ACTIVE_OLDER_ADULT_65"
    )