from datetime import date

from app.domain.ymca_schemas import DaxkoRawRow
from app.services.ymca_case_store import InMemoryMemberCaseStore
from app.services.ymca_workflow_execution_service import YmcaWorkflowExecutionService


def make_raw_row(**overrides):
    base = {
        "member_id": "MEM-1",
        "membership_id": "M-1",
        "first_name": "Emily",
        "last_name": "Carter",
        "branch_code": "54",
        "branch_name": "Easton YMCA",
        "membership_type": "Teen",
        "membership_status": "Active",
        "member_status": "Active",
        "dob": date(2007, 4, 14),
        "email": "emily@example.com",
        "phone": "555-1234",
        "address1": "123 Main St",
        "address2": None,
        "city": "Easton",
        "state": "PA",
        "zip": "18042",
        "country": "US",
    }
    base.update(overrides)
    return DaxkoRawRow(**base)


def test_execution_creates_and_persists_case_for_eligible_row():
    store = InMemoryMemberCaseStore()
    service = YmcaWorkflowExecutionService(store=store)

    raw = make_raw_row(membership_type="Teen", dob=date(2007, 4, 14))
    result = service.run(raw)

    assert result.evaluation_result.decision == "ELIGIBLE"
    assert result.case_creation_decision.should_create_case is True
    assert result.store_result is not None
    assert result.store_result.created is True
    assert result.store_result.reason == "CASE_CREATED"


def test_execution_creates_and_persists_case_for_needs_enrichment_row():
    store = InMemoryMemberCaseStore()
    service = YmcaWorkflowExecutionService(store=store)

    raw = make_raw_row(membership_type="Family 2", dob=date(1998, 4, 14))
    result = service.run(raw)

    assert result.evaluation_result.decision == "NEEDS_ENRICHMENT"
    assert result.case_creation_decision.should_create_case is True
    assert result.store_result is not None
    assert result.store_result.created is True
    assert "HOUSEHOLD_MEMBER_LOOKUP" in result.evaluation_result.enrichment_required


def test_execution_does_not_persist_excluded_row():
    store = InMemoryMemberCaseStore()
    service = YmcaWorkflowExecutionService(store=store)

    raw = make_raw_row(membership_type="Employee Teen", dob=date(2007, 4, 14))
    result = service.run(raw)

    assert result.evaluation_result.decision == "EXCLUDED"
    assert result.case_creation_decision.should_create_case is False
    assert result.store_result is None


def test_execution_is_idempotent_for_same_semantic_case():
    store = InMemoryMemberCaseStore()
    service = YmcaWorkflowExecutionService(store=store)

    raw = make_raw_row(
        member_id="MEM-42",
        membership_id="M-99",
        membership_type="Teen",
        dob=date(2007, 4, 14),
    )

    first = service.run(raw)
    second = service.run(raw)

    assert first.store_result is not None
    assert first.store_result.created is True

    assert second.store_result is not None
    assert second.store_result.created is False
    assert second.store_result.reason == "CASE_ALREADY_EXISTS"