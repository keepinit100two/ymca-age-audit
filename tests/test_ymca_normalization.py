import pytest
from datetime import date

from app.domain.ymca_schemas import DaxkoRawRow
from app.services.ymca_normalizer import YmcaNormalizationService


def make_base_row(**overrides):
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


def test_full_name_composition():
    raw = make_base_row()
    svc = YmcaNormalizationService()

    member, membership, snapshot, flags = svc.normalize(raw)

    assert member.full_name == "Emily Carter"


def test_branch_canonicalization():
    raw = make_base_row(branch_name="Easton YMCA")
    svc = YmcaNormalizationService()

    member, membership, snapshot, flags = svc.normalize(raw)

    assert member.branch_id == "easton"
    assert membership.branch_id == "easton"


@pytest.mark.parametrize(
    "branch_name, expected_branch_id",
    [
        ("Easton YMCA", "easton"),
        ("Quakertown PA YMCA", "quakertown"),
        ("Warminster PA YMCA", "warminster"),
        ("Nazareth PA", "nazareth"),
        ("Slate Belt branch (Pen Argyl PA)", "slate_belt"),
        ("Fairless Hills PA", "fairless_hills"),
        ("Bethlehem YMCA", "bethlehem"),
        ("Doylestown YMCA", "doylestown"),
    ],
)
def test_known_branch_canonicalization(branch_name, expected_branch_id):
    raw = make_base_row(branch_name=branch_name)
    svc = YmcaNormalizationService()

    member, membership, snapshot, flags = svc.normalize(raw)

    assert member.branch_id == expected_branch_id
    assert membership.branch_id == expected_branch_id
    assert snapshot.branch_id == expected_branch_id


def test_unknown_branch_falls_back_to_unknown():
    raw = make_base_row(branch_name="Mystery Branch")
    svc = YmcaNormalizationService()

    member, membership, snapshot, flags = svc.normalize(raw)

    assert member.branch_id == "unknown"
    assert membership.branch_id == "unknown"
    assert snapshot.branch_id == "unknown"


def test_contactable_by_email_true():
    raw = make_base_row(email="test@example.com")
    svc = YmcaNormalizationService()

    _, _, snapshot, flags = svc.normalize(raw)

    assert flags.contactable_by_email is True
    assert snapshot.contactable_by_email is True


def test_contactable_by_email_false_when_missing():
    raw = make_base_row(email=None)
    svc = YmcaNormalizationService()

    _, _, snapshot, flags = svc.normalize(raw)

    assert flags.contactable_by_email is False
    assert snapshot.contactable_by_email is False


def test_family_membership_flag():
    raw = make_base_row(membership_type="Family 2")
    svc = YmcaNormalizationService()

    _, _, _, flags = svc.normalize(raw)

    assert flags.is_family_membership is True


def test_employee_membership_flag():
    raw = make_base_row(membership_type="Employee Teen")
    svc = YmcaNormalizationService()

    _, _, _, flags = svc.normalize(raw)

    assert flags.is_employee_membership is True


def test_turning_age_derivation():
    raw = make_base_row(dob=date(2007, 4, 14))
    svc = YmcaNormalizationService()

    _, _, snapshot, flags = svc.normalize(raw)

    assert snapshot.turning_age == 19
    assert flags.turning_age == 19
    
def test_branch_mapping_is_loaded_from_config():
    svc = YmcaNormalizationService()

    assert svc.branch_mapping["easton ymca"] == "easton"
    assert svc.branch_mapping["bethlehem ymca"] == "bethlehem"