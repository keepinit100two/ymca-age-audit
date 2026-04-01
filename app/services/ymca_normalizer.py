from datetime import datetime, date

from app.domain.ymca_schemas import (
    DaxkoRawRow,
    MemberRecord,
    MembershipRecord,
    MemberStateSnapshot,
    DerivedFlags,
)


class YmcaNormalizationService:
    def normalize(self, raw: DaxkoRawRow):
        """
        Initial deterministic normalization slice:
        - full name composition
        - full known branch canonicalization
        - basic email contactability
        - membership-type derived flags
        - simple turning-age derivation

        Rules:
        - Pure function (no side effects)
        - Deterministic
        - No external calls
        - No database writes
        """

        branch_id = self._normalize_branch(raw.branch_name)
        full_name = self._compose_full_name(raw.first_name, raw.last_name)
        contactable_by_email = self._derive_contactable_by_email(raw.email)

        membership_type_raw = raw.membership_type or ""
        member_status = raw.member_status or "unknown"
        membership_status = raw.membership_status or "unknown"

        flags = DerivedFlags(
            is_family_membership=self._is_family_membership(membership_type_raw),
            is_employee_membership=self._is_employee_membership(membership_type_raw),
            is_two_adult_membership=self._is_two_adult_membership(membership_type_raw),
            contactable_by_email=contactable_by_email,
            turning_age=self._calculate_turning_age(raw.dob),
        )

        member = MemberRecord(
            member_id=raw.member_id,
            full_name=full_name,
            email=raw.email,
            phone=raw.phone,
            address1=raw.address1,
            address2=raw.address2,
            city=raw.city,
            state=raw.state,
            zip=raw.zip,
            country=raw.country,
            branch_id=branch_id,
        )

        membership = MembershipRecord(
            membership_id=raw.membership_id,
            membership_type=membership_type_raw or "unknown",
            membership_status=membership_status,
            branch_id=branch_id,
        )

        snapshot = MemberStateSnapshot(
            snapshot_id="temp",
            member_id=raw.member_id,
            membership_id=raw.membership_id,
            branch_id=branch_id,
            membership_type_current=membership_type_raw or "unknown",
            member_status=member_status,
            membership_status=membership_status,
            turning_age=flags.turning_age,
            contactable_by_email=contactable_by_email,
            email=raw.email,
            observed_at=datetime.utcnow(),
        )

        return member, membership, snapshot, flags

    def _compose_full_name(self, first_name: str, last_name: str) -> str:
        return f"{first_name.strip()} {last_name.strip()}".strip()

    def _derive_contactable_by_email(self, email: str | None) -> bool:
        return bool(email and email.strip())

    def _is_family_membership(self, membership_type: str) -> bool:
        normalized = membership_type.lower()
        return "family" in normalized

    def _is_employee_membership(self, membership_type: str) -> bool:
        normalized = membership_type.lower()
        return "employee" in normalized

    def _is_two_adult_membership(self, membership_type: str) -> bool:
        normalized = membership_type.lower()
        return "2 adult" in normalized or "two adult" in normalized

    def _normalize_branch(self, branch_name: str | None) -> str:
        if not branch_name:
            return "unknown"

        normalized = branch_name.strip().lower()

        if "quakertown" in normalized:
            return "quakertown"
        if "warminster" in normalized:
            return "warminster"
        if "nazareth" in normalized:
            return "nazareth"
        if "slate belt" in normalized or "pen argyl" in normalized:
            return "slate_belt"
        if "fairless hills" in normalized:
            return "fairless_hills"
        if "easton" in normalized:
            return "easton"
        if "bethlehem" in normalized:
            return "bethlehem"
        if "doylestown" in normalized:
            return "doylestown"

        return "unknown"

    def _calculate_turning_age(self, dob: date | None) -> int | None:
        if dob is None:
            return None

        today = date.today()
        return today.year - dob.year