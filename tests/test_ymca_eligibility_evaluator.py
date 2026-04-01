from datetime import datetime

from app.domain.ymca_schemas import (
    MemberRecord,
    MembershipRecord,
    MemberStateSnapshot,
    DerivedFlags,
    TransitionClassification,
)
from app.services.ymca_eligibility_evaluator import YmcaEligibilityEvaluator


def make_objects(
    *,
    membership_type="Teen",
    membership_status="Active",
    member_status="Active",
    is_family_membership=False,
    is_employee_membership=False,
    is_two_adult_membership=False,
    turning_age=19,
    transition_type="TEEN_TO_YOUNG_ADULT_19",
    target_membership_type="Young Adult",
    in_scope=True,
    out_of_scope_reason=None,
):
    member = MemberRecord(
        member_id="MEM-1",
        full_name="Emily Carter",
        email="emily@example.com",
        phone="555-1234",
        address1="123 Main St",
        address2=None,
        city="Easton",
        state="PA",
        zip="18042",
        country="US",
        branch_id="easton",
    )

    membership = MembershipRecord(
        membership_id="M-1",
        membership_type=membership_type,
        membership_status=membership_status,
        branch_id="easton",
    )

    snapshot = MemberStateSnapshot(
        snapshot_id="snap-1",
        member_id="MEM-1",
        membership_id="M-1",
        branch_id="easton",
        membership_type_current=membership_type,
        member_status=member_status,
        membership_status=membership_status,
        turning_age=turning_age,
        contactable_by_email=True,
        email="emily@example.com",
        observed_at=datetime.utcnow(),
    )

    flags = DerivedFlags(
        is_family_membership=is_family_membership,
        is_employee_membership=is_employee_membership,
        is_two_adult_membership=is_two_adult_membership,
        contactable_by_email=True,
        turning_age=turning_age,
    )

    transition = TransitionClassification(
        transition_type=transition_type,
        target_membership_type=target_membership_type,
        in_scope=in_scope,
        out_of_scope_reason=out_of_scope_reason,
    )

    return member, membership, snapshot, flags, transition


def test_active_member_is_eligible():
    objs = make_objects()
    result = YmcaEligibilityEvaluator().evaluate(*objs)

    assert result["decision"] == "ELIGIBLE"
    assert result["exclusion_codes"] == []
    assert result["enrichment_required"] == []


def test_employee_is_excluded():
    objs = make_objects(
        membership_type="Employee Teen",
        is_employee_membership=True,
        transition_type="TEEN_TO_YOUNG_ADULT_19",
        target_membership_type="Young Adult",
    )
    result = YmcaEligibilityEvaluator().evaluate(*objs)

    assert result["decision"] == "EXCLUDED"
    assert "EXCLUDED_EMPLOYEE" in result["exclusion_codes"]
    assert result["enrichment_required"] == []


def test_inactive_member_is_excluded():
    objs = make_objects(member_status="Inactive")
    result = YmcaEligibilityEvaluator().evaluate(*objs)

    assert result["decision"] == "EXCLUDED"
    assert "EXCLUDED_NOT_ACTIVE" in result["exclusion_codes"]
    assert result["enrichment_required"] == []


def test_inactive_membership_is_excluded():
    objs = make_objects(membership_status="Inactive")
    result = YmcaEligibilityEvaluator().evaluate(*objs)

    assert result["decision"] == "EXCLUDED"
    assert "EXCLUDED_NOT_ACTIVE" in result["exclusion_codes"]
    assert result["enrichment_required"] == []


def test_family_28_requires_enrichment():
    objs = make_objects(
        membership_type="Family 2",
        is_family_membership=True,
        turning_age=28,
        transition_type="FAMILY_DEPENDENT_AGE_OUT_28",
        target_membership_type=None,
    )
    result = YmcaEligibilityEvaluator().evaluate(*objs)

    assert result["decision"] == "NEEDS_ENRICHMENT"
    assert result["exclusion_codes"] == []
    assert "HOUSEHOLD_MEMBER_LOOKUP" in result["enrichment_required"]


def test_two_adult_65_requires_enrichment():
    objs = make_objects(
        membership_type="2 Adult",
        is_two_adult_membership=True,
        turning_age=65,
        transition_type="TWO_ADULT_TO_TWO_ACTIVE_OLDER_ADULTS_65",
        target_membership_type="2 Active Older Adults",
    )
    result = YmcaEligibilityEvaluator().evaluate(*objs)

    assert result["decision"] == "NEEDS_ENRICHMENT"
    assert result["exclusion_codes"] == []
    assert "HOUSEHOLD_MEMBER_LOOKUP" in result["enrichment_required"]


def test_out_of_scope_transition_is_excluded():
    objs = make_objects(
        membership_type="Corporate Wellness",
        turning_age=19,
        transition_type=None,
        target_membership_type=None,
        in_scope=False,
        out_of_scope_reason="NO_SUPPORTED_TRANSITION_MATCH",
    )
    result = YmcaEligibilityEvaluator().evaluate(*objs)

    assert result["decision"] == "EXCLUDED"
    assert "EXCLUDED_UNKNOWN" in result["exclusion_codes"]
    assert result["enrichment_required"] == []


def test_youth_13_transition_is_eligible():
    objs = make_objects(
        membership_type="Youth 1",
        turning_age=13,
        transition_type="YOUTH_TO_TEEN_13",
        target_membership_type="Teen",
    )
    result = YmcaEligibilityEvaluator().evaluate(*objs)

    assert result["decision"] == "ELIGIBLE"
    assert result["exclusion_codes"] == []
    assert result["enrichment_required"] == []


def test_young_adult_28_transition_is_eligible():
    objs = make_objects(
        membership_type="Young Adult",
        turning_age=28,
        transition_type="YOUNG_ADULT_TO_ADULT_28",
        target_membership_type="Adult",
    )
    result = YmcaEligibilityEvaluator().evaluate(*objs)

    assert result["decision"] == "ELIGIBLE"
    assert result["exclusion_codes"] == []
    assert result["enrichment_required"] == []


def test_adult_65_transition_is_eligible():
    objs = make_objects(
        membership_type="Adult",
        turning_age=65,
        transition_type="ADULT_TO_ACTIVE_OLDER_ADULT_65",
        target_membership_type="Active Older Adult",
    )
    result = YmcaEligibilityEvaluator().evaluate(*objs)

    assert result["decision"] == "ELIGIBLE"
    assert result["exclusion_codes"] == []
    assert result["enrichment_required"] == []