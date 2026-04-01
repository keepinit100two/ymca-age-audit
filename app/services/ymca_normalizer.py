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
        Convert raw Daxko row into canonical domain models.

        Rules:
        - Pure function (no side effects)
        - Deterministic
        - No external calls
        - No database writes
        """

        raise NotImplementedError("Normalization logic not implemented yet")