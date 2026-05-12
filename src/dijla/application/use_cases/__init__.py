"""Use cases — each one expresses a single user / system intent."""

from dijla.application.use_cases.list_cycles import ListCyclesUseCase
from dijla.application.use_cases.list_hypotheses import ListHypothesesUseCase
from dijla.application.use_cases.list_theorems import ListTheoremsUseCase
from dijla.application.use_cases.query_knowledge_graph import QueryKnowledgeGraphUseCase
from dijla.application.use_cases.resume_cycle import ResumeCycleUseCase
from dijla.application.use_cases.start_cycle import StartCycleUseCase
from dijla.application.use_cases.submit_hypothesis import SubmitHypothesisUseCase

__all__ = [
    "ListCyclesUseCase",
    "ListHypothesesUseCase",
    "ListTheoremsUseCase",
    "QueryKnowledgeGraphUseCase",
    "ResumeCycleUseCase",
    "StartCycleUseCase",
    "SubmitHypothesisUseCase",
]
