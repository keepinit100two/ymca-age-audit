from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime, date


# -------------------------
# RAW SOURCE CONTRACT
# -------------------------

class DaxkoRawRow(BaseModel):
    member_id: str
    membership_id: str

    first_name: str
    last_name: str

    branch_code: Optional[str]
    branch_name: Optional[str]

    membership_type: Optional[str]
    membership_status: Optional[str]
    member_status: Optional[str]

    dob: Optional[date]

    email: Optional[str]
    phone: Optional[str]

    address1: Optional[str]
    address2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]
    country: Optional[str]


# -------------------------
# CANONICAL DOMAIN MODELS
# -------------------------

class MemberRecord(BaseModel):
    member_id: str
    full_name: str

    email: Optional[str]
    phone: Optional[str]

    address1: Optional[str]
    address2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]
    country: Optional[str]

    branch_id: str


class MembershipRecord(BaseModel):
    membership_id: str
    membership_type: str
    membership_status: str
    branch_id: str


class MemberStateSnapshot(BaseModel):
    snapshot_id: str

    member_id: str
    membership_id: str
    branch_id: str

    membership_type_current: str

    member_status: str
    membership_status: str

    turning_age: Optional[int]

    contactable_by_email: bool
    email: Optional[str]

    observed_at: datetime


# -------------------------
# DERIVED FLAGS
# -------------------------

class DerivedFlags(BaseModel):
    is_family_membership: bool
    is_employee_membership: bool
    is_two_adult_membership: bool

    contactable_by_email: bool

    turning_age: Optional[int]


# -------------------------
# ENUMS / CONTROL VALUES
# -------------------------

TransitionType = Literal[
    "YOUTH_TO_TEEN_13",
    "TEEN_TO_YOUNG_ADULT_19",
    "YOUNG_ADULT_TO_ADULT_28",
    "FAMILY_DEPENDENT_AGE_OUT_28",
    "ADULT_TO_ACTIVE_OLDER_ADULT_65",
    "TWO_ADULT_TO_TWO_ACTIVE_OLDER_ADULTS_65",
]

ExclusionCode = Literal[
    "EXCLUDED_EMPLOYEE",
    "EXCLUDED_FAMILY_PRIMARY_28",
    "EXCLUDED_TWO_ADULT_SECOND_NOT_65",
    "EXCLUDED_NOT_ACTIVE",
    "EXCLUDED_NO_CONTACT",
    "EXCLUDED_UNKNOWN",
]

EligibilityDecision = Literal[
    "ELIGIBLE",
    "EXCLUDED",
    "NEEDS_ENRICHMENT",
]

EnrichmentType = Literal[
    "HOUSEHOLD_MEMBER_LOOKUP",
]


class TransitionClassification(BaseModel):
    transition_type: Optional[TransitionType]
    target_membership_type: Optional[str]
    in_scope: bool
    out_of_scope_reason: Optional[str]