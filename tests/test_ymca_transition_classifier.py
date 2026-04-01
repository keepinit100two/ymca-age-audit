from datetime import datetime

from app.domain.ymca_schemas import (
    MembershipRecord,
    MemberStateSnapshot,
    DerivedFlags,
)
from app.services.ymca_transition_classifier import YmcaTransitionClassifier


def make_objects(
    *,
    membership_type="Teen",
    membership_status="Active",
    member_status="Active",
    turning_age=19,
    is_family_membership=False,
    is_employee_membership=False,
    is_two_adult_membership=False,
):
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

    return membership, snapshot, flags


def test_youth_to_teen_transition():
    objs = make_objects(membership_type="Youth 1", turning_age=13)
    result = YmcaTransitionClassifier().classify(*objs)

    assert result.in_scope is True
    assert result.transition_type == "YOUTH_TO_TEEN_13"
    assert result.target_membership_type == "Teen"


def test_teen_to_young_adult_transition():
    objs = make_objects(membership_type="Teen", turning_age=19)
    result = YmcaTransitionClassifier().classify(*objs)

    assert result.in_scope is True
    assert result.transition_type == "TEEN_TO_YOUNG_ADULT_19"
    assert result.target_membership_type == "Young Adult"


def test_employee_teen_to_young_adult_transition():
    objs = make_objects(
        membership_type="Employee Teen",
        turning_age=19,
        is_employee_membership=True,
    )
    result = YmcaTransitionClassifier().classify(*objs)

    assert result.in_scope is True
    assert result.transition_type == "TEEN_TO_YOUNG_ADULT_19"
    assert result.target_membership_type == "Young Adult"


def test_fitness_express_teen_to_young_adult_transition():
    objs = make_objects(membership_type="Fitness Express Teen", turning_age=19)
    result = YmcaTransitionClassifier().classify(*objs)

    assert result.in_scope is True
    assert result.transition_type == "TEEN_TO_YOUNG_ADULT_19"


def test_young_adult_to_adult_transition():
    objs = make_objects(membership_type="Young Adult", turning_age=28)
    result = YmcaTransitionClassifier().classify(*objs)

    assert result.in_scope is True
    assert result.transition_type == "YOUNG_ADULT_TO_ADULT_28"
    assert result.target_membership_type == "Adult"


def test_family_dependent_age_out_transition():
    objs = make_objects(
        membership_type="Family 2",
        turning_age=28,
        is_family_membership=True,
    )
    result = YmcaTransitionClassifier().classify(*objs)

    assert result.in_scope is True
    assert result.transition_type == "FAMILY_DEPENDENT_AGE_OUT_28"
    assert result.target_membership_type is None


def test_adult_to_active_older_adult_transition():
    objs = make_objects(membership_type="Adult", turning_age=65)
    result = YmcaTransitionClassifier().classify(*objs)

    assert result.in_scope is True
    assert result.transition_type == "ADULT_TO_ACTIVE_OLDER_ADULT_65"
    assert result.target_membership_type == "Active Older Adult"


def test_employee_adult_to_active_older_adult_transition():
    objs = make_objects(
        membership_type="Employee Adult",
        turning_age=65,
        is_employee_membership=True,
    )
    result = YmcaTransitionClassifier().classify(*objs)

    assert result.in_scope is True
    assert result.transition_type == "ADULT_TO_ACTIVE_OLDER_ADULT_65"


def test_two_adult_transition():
    objs = make_objects(
        membership_type="2 Adult",
        turning_age=65,
        is_two_adult_membership=True,
    )
    result = YmcaTransitionClassifier().classify(*objs)

    assert result.in_scope is True
    assert result.transition_type == "TWO_ADULT_TO_TWO_ACTIVE_OLDER_ADULTS_65"
    assert result.target_membership_type == "2 Active Older Adults"


def test_out_of_scope_membership_type():
    objs = make_objects(membership_type="Corporate Wellness", turning_age=19)
    result = YmcaTransitionClassifier().classify(*objs)

    assert result.in_scope is False
    assert result.transition_type is None
    assert result.out_of_scope_reason == "NO_SUPPORTED_TRANSITION_MATCH"