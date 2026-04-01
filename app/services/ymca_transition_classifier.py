from app.domain.ymca_schemas import (
    MembershipRecord,
    MemberStateSnapshot,
    DerivedFlags,
    TransitionClassification,
)


class YmcaTransitionClassifier:
    def classify(
        self,
        membership: MembershipRecord,
        snapshot: MemberStateSnapshot,
        flags: DerivedFlags,
    ) -> TransitionClassification:
        membership_type = (membership.membership_type or "").strip().lower()
        turning_age = flags.turning_age

        if turning_age == 13 and membership_type in {
            "youth 1",
            "youth 2",
            "youth 3",
        }:
            return TransitionClassification(
                transition_type="YOUTH_TO_TEEN_13",
                target_membership_type="Teen",
                in_scope=True,
                out_of_scope_reason=None,
            )

        if turning_age == 19 and membership_type in {
            "teen",
            "employee teen",
            "fitness express teen",
        }:
            return TransitionClassification(
                transition_type="TEEN_TO_YOUNG_ADULT_19",
                target_membership_type="Young Adult",
                in_scope=True,
                out_of_scope_reason=None,
            )

        if turning_age == 28 and membership_type in {
            "young adult",
        }:
            return TransitionClassification(
                transition_type="YOUNG_ADULT_TO_ADULT_28",
                target_membership_type="Adult",
                in_scope=True,
                out_of_scope_reason=None,
            )

        if turning_age == 28 and flags.is_family_membership:
            return TransitionClassification(
                transition_type="FAMILY_DEPENDENT_AGE_OUT_28",
                target_membership_type=None,
                in_scope=True,
                out_of_scope_reason=None,
            )

        if turning_age == 65 and membership_type in {
            "adult",
            "employee adult",
        }:
            return TransitionClassification(
                transition_type="ADULT_TO_ACTIVE_OLDER_ADULT_65",
                target_membership_type="Active Older Adult",
                in_scope=True,
                out_of_scope_reason=None,
            )

        if turning_age == 65 and flags.is_two_adult_membership:
            return TransitionClassification(
                transition_type="TWO_ADULT_TO_TWO_ACTIVE_OLDER_ADULTS_65",
                target_membership_type="2 Active Older Adults",
                in_scope=True,
                out_of_scope_reason=None,
            )

        return TransitionClassification(
            transition_type=None,
            target_membership_type=None,
            in_scope=False,
            out_of_scope_reason="NO_SUPPORTED_TRANSITION_MATCH",
        )