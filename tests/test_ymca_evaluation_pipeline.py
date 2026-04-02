from datetime import date

from app.domain.ymca_schemas import DaxkoRawRow
from app.services.ymca_evaluation_pipeline import YmcaEvaluationPipeline


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


def test_pipeline_returns_eligible_result():
    raw = make_raw_row(membership_type="Teen", dob=date(2007, 4, 14))
    result = YmcaEvaluationPipeline().run(raw)

    assert result.member_id == "MEM-1"
    assert result.membership_id == "M-1"
    assert result.branch_id == "easton"
    assert result.transition_type == "TEEN_TO_YOUNG_ADULT_19"
    assert result.target_membership_type == "Young Adult"
    assert result.decision == "ELIGIBLE"
    assert result.exclusion_codes == []
    assert result.enrichment_required == []
    assert result.in_scope is True
    assert result.out_of_scope_reason is None


def test_pipeline_returns_excluded_result_for_employee_membership():
    raw = make_raw_row(
        membership_type="Employee Teen",
        dob=date(2007, 4, 14),
    )
    result = YmcaEvaluationPipeline().run(raw)

    assert result.transition_type == "TEEN_TO_YOUNG_ADULT_19"
    assert result.decision == "EXCLUDED"
    assert "EXCLUDED_EMPLOYEE" in result.exclusion_codes
    assert result.enrichment_required == []


def test_pipeline_returns_needs_enrichment_for_family_28():
    raw = make_raw_row(
        membership_type="Family 2",
        dob=date(1998, 4, 14),
    )
    result = YmcaEvaluationPipeline().run(raw)

    assert result.transition_type == "FAMILY_DEPENDENT_AGE_OUT_28"
    assert result.decision == "NEEDS_ENRICHMENT"
    assert "HOUSEHOLD_MEMBER_LOOKUP" in result.enrichment_required


def test_pipeline_returns_out_of_scope_result():
    raw = make_raw_row(
        membership_type="Corporate Wellness",
        dob=date(2007, 4, 14),
    )
    result = YmcaEvaluationPipeline().run(raw)

    assert result.transition_type is None
    assert result.target_membership_type is None
    assert result.decision == "EXCLUDED"
    assert "EXCLUDED_UNKNOWN" in result.exclusion_codes
    assert result.in_scope is False
    assert result.out_of_scope_reason == "NO_SUPPORTED_TRANSITION_MATCH"