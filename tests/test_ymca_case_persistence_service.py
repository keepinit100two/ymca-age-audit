from app.domain.ymca_schemas import YmcaEvaluationResult
from app.services.ymca_case_store import InMemoryMemberCaseStore
from app.services.ymca_case_persistence_service import YmcaCasePersistenceService


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


def test_persist_creates_new_case_for_eligible_result():
    store = InMemoryMemberCaseStore()
    service = YmcaCasePersistenceService(store=store)

    result = make_result(decision="ELIGIBLE")
    case_decision, store_result = service.persist_from_evaluation(result)

    assert case_decision.should_create_case is True
    assert store_result is not None
    assert store_result.created is True
    assert store_result.reason == "CASE_CREATED"
    assert store_result.case.identity.member_id == "MEM-1"


def test_persist_creates_new_case_for_needs_enrichment_result():
    store = InMemoryMemberCaseStore()
    service = YmcaCasePersistenceService(store=store)

    result = make_result(
        transition_type="FAMILY_DEPENDENT_AGE_OUT_28",
        target_membership_type=None,
        decision="NEEDS_ENRICHMENT",
        enrichment_required=["HOUSEHOLD_MEMBER_LOOKUP"],
    )
    case_decision, store_result = service.persist_from_evaluation(result)

    assert case_decision.should_create_case is True
    assert store_result is not None
    assert store_result.created is True
    assert "HOUSEHOLD_MEMBER_LOOKUP" in store_result.case.qualification.enrichment_required


def test_duplicate_semantic_key_does_not_create_second_case():
    store = InMemoryMemberCaseStore()
    service = YmcaCasePersistenceService(store=store)

    result = make_result(
        member_id="MEM-42",
        membership_id="M-99",
        transition_type="ADULT_TO_ACTIVE_OLDER_ADULT_65",
        decision="ELIGIBLE",
    )

    first_decision, first_store_result = service.persist_from_evaluation(result)
    second_decision, second_store_result = service.persist_from_evaluation(result)

    assert first_decision.should_create_case is True
    assert first_store_result is not None
    assert first_store_result.created is True

    assert second_decision.should_create_case is True
    assert second_store_result is not None
    assert second_store_result.created is False
    assert second_store_result.reason == "CASE_ALREADY_EXISTS"
    assert (
        second_store_result.case.identity.case_semantic_key
        == first_store_result.case.identity.case_semantic_key
    )


def test_excluded_result_does_not_persist_case():
    store = InMemoryMemberCaseStore()
    service = YmcaCasePersistenceService(store=store)

    result = make_result(
        decision="EXCLUDED",
        exclusion_codes=["EXCLUDED_EMPLOYEE"],
    )
    case_decision, store_result = service.persist_from_evaluation(result)

    assert case_decision.should_create_case is False
    assert store_result is None


def test_out_of_scope_result_does_not_persist_case():
    store = InMemoryMemberCaseStore()
    service = YmcaCasePersistenceService(store=store)

    result = make_result(
        transition_type=None,
        target_membership_type=None,
        decision="EXCLUDED",
        exclusion_codes=["EXCLUDED_UNKNOWN"],
        in_scope=False,
        out_of_scope_reason="NO_SUPPORTED_TRANSITION_MATCH",
    )
    case_decision, store_result = service.persist_from_evaluation(result)

    assert case_decision.should_create_case is False
    assert store_result is None