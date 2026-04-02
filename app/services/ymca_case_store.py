from abc import ABC, abstractmethod

from app.domain.ymca_schemas import MemberCase, MemberCaseStoreResult


class MemberCaseStore(ABC):
    @abstractmethod
    def get_by_semantic_key(self, case_semantic_key: str) -> MemberCase | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, case: MemberCase) -> MemberCaseStoreResult:
        raise NotImplementedError


class InMemoryMemberCaseStore(MemberCaseStore):
    def __init__(self):
        self._cases_by_semantic_key: dict[str, MemberCase] = {}

    def get_by_semantic_key(self, case_semantic_key: str) -> MemberCase | None:
        return self._cases_by_semantic_key.get(case_semantic_key)

    def create(self, case: MemberCase) -> MemberCaseStoreResult:
        existing = self.get_by_semantic_key(case.identity.case_semantic_key)
        if existing is not None:
            return MemberCaseStoreResult(
                created=False,
                case=existing,
                reason="CASE_ALREADY_EXISTS",
            )

        self._cases_by_semantic_key[case.identity.case_semantic_key] = case
        return MemberCaseStoreResult(
            created=True,
            case=case,
            reason="CASE_CREATED",
        )