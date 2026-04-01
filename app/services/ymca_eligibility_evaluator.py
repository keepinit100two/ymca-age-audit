import json
from pathlib import Path

from app.domain.ymca_schemas import (
    MemberRecord,
    MembershipRecord,
    MemberStateSnapshot,
    DerivedFlags,
    TransitionClassification,
    EnrichmentType,
)


class YmcaEligibilityEvaluator:
    def __init__(self, rules_path: str | None = None):
        self.rules = self._load_rules(rules_path)
        self.exclusion_rules = self.rules.get("exclusion_rules", {})

    def evaluate(
        self,
        member: MemberRecord,
        membership: MembershipRecord,
        snapshot: MemberStateSnapshot,
        flags: DerivedFlags,
        transition: TransitionClassification,
    ) -> dict:
        """
        Returns:
        {
            "decision": "ELIGIBLE" | "EXCLUDED" | "NEEDS_ENRICHMENT",
            "exclusion_codes": [],
            "enrichment_required": []
        }
        """

        exclusion_codes: list[str] = []
        enrichment_required: list[EnrichmentType] = []

        # -------------------------
        # OUT-OF-SCOPE TRANSITIONS
        # -------------------------
        if not transition.in_scope:
            return {
                "decision": "EXCLUDED",
                "exclusion_codes": ["EXCLUDED_UNKNOWN"],
                "enrichment_required": [],
            }

        # -------------------------
        # HARD EXCLUSIONS (safe)
        # -------------------------
        if self._exclude_employee_memberships_enabled() and flags.is_employee_membership:
            exclusion_codes.append("EXCLUDED_EMPLOYEE")

        if not self._is_active_member_status(snapshot.member_status):
            exclusion_codes.append("EXCLUDED_NOT_ACTIVE")

        if not self._is_active_membership_status(snapshot.membership_status):
            exclusion_codes.append("EXCLUDED_NOT_ACTIVE")

        if exclusion_codes:
            return {
                "decision": "EXCLUDED",
                "exclusion_codes": exclusion_codes,
                "enrichment_required": [],
            }

        # -------------------------
        # ENRICHMENT-REQUIRED TRANSITIONS
        # -------------------------
        if transition.transition_type in {
            "FAMILY_DEPENDENT_AGE_OUT_28",
            "TWO_ADULT_TO_TWO_ACTIVE_OLDER_ADULTS_65",
        }:
            enrichment_required.append("HOUSEHOLD_MEMBER_LOOKUP")

        if enrichment_required:
            return {
                "decision": "NEEDS_ENRICHMENT",
                "exclusion_codes": [],
                "enrichment_required": enrichment_required,
            }

        # -------------------------
        # DEFAULT ELIGIBLE
        # -------------------------
        return {
            "decision": "ELIGIBLE",
            "exclusion_codes": [],
            "enrichment_required": [],
        }

    def _load_rules(self, rules_path: str | None) -> dict:
        path = Path(rules_path) if rules_path else Path("configs/ymca_rules.json")
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _exclude_employee_memberships_enabled(self) -> bool:
        return bool(self.exclusion_rules.get("exclude_employee_memberships", False))

    def _is_active_member_status(self, member_status: str) -> bool:
        allowed = self.exclusion_rules.get("active_member_statuses", [])
        return member_status.strip().lower() in allowed

    def _is_active_membership_status(self, membership_status: str) -> bool:
        allowed = self.exclusion_rules.get("active_membership_statuses", [])
        return membership_status.strip().lower() in allowed