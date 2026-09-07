from enum import Enum


class Treatment(Enum):
    WITH_AI = "with_ai"
    WITHOUT_AI = "without_ai"


class ResearchQuestion(Enum):
    RQ1 = "RQ1"
    RQ2 = "RQ2"
    RQ3 = "RQ3"


class HypothesisType(Enum):
    NULL = "H0"
    ALTERNATIVE = "H1"


class VariableType(Enum):
    INDEPENDENT = "independent"
    DEPENDENT = "dependent"
    CONTROL = "control"


class ThreatCategory(Enum):
    INTERNAL_VALIDITY = "internal_validity"
    EXTERNAL_VALIDITY = "external_validity"
    STATISTICAL_CONCLUSION = "statistical_conclusion"
    CONSTRUCT_VALIDITY = "construct_validity"
