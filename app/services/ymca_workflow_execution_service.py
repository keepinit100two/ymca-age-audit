from app.domain.ymca_schemas import DaxkoRawRow, YmcaExecutionResult
from app.services.ymca_evaluation_pipeline import YmcaEvaluationPipeline
from app.services.ymca_case_persistence_service import YmcaCasePersistenceService
from app.services.ymca_case_store import MemberCaseStore


class YmcaWorkflowExecutionService:
    def __init__(
        self,
        store: MemberCaseStore,
        evaluation_pipeline: YmcaEvaluationPipeline | None = None,
        persistence_service: YmcaCasePersistenceService | None = None,
    ):
        self.store = store
        self.evaluation_pipeline = evaluation_pipeline or YmcaEvaluationPipeline()
        self.persistence_service = persistence_service or YmcaCasePersistenceService(
            store=store
        )

    def run(self, raw: DaxkoRawRow) -> YmcaExecutionResult:
        evaluation_result = self.evaluation_pipeline.run(raw)
        case_creation_decision, store_result = self.persistence_service.persist_from_evaluation(
            evaluation_result
        )

        return YmcaExecutionResult(
            evaluation_result=evaluation_result,
            case_creation_decision=case_creation_decision,
            store_result=store_result,
        )