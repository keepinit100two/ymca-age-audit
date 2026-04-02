from app.domain.ymca_schemas import (
    YmcaEvaluationResult,
    CaseCreationDecision,
    MemberCaseStoreResult,
)
from app.services.ymca_case_builder import YmcaCaseBuilder
from app.services.ymca_case_store import MemberCaseStore


class YmcaCasePersistenceService:
    def __init__(
        self,
        store: MemberCaseStore,
        case_builder: YmcaCaseBuilder | None = None,
    ):
        self.store = store
        self.case_builder = case_builder or YmcaCaseBuilder()

    def persist_from_evaluation(
        self,
        result: YmcaEvaluationResult,
    ) -> tuple[CaseCreationDecision, MemberCaseStoreResult | None]:
        case_decision = self.case_builder.build_case_decision(result)

        if not case_decision.should_create_case or case_decision.case is None:
            return case_decision, None

        store_result = self.store.create(case_decision.case)
        return case_decision, store_result