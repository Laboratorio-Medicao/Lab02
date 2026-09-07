import pytest

from experiment.config.lab02_design import N_KATAS, PARTICIPANTS, TIME_BOX_MINUTES, create_lab02_design
from experiment.domain.enums import (
    HypothesisType,
    ResearchQuestion,
    ThreatCategory,
    Treatment,
    VariableType,
)


@pytest.fixture
def design():
    return create_lab02_design()


class TestHypotheses:
    def test_all_research_questions_have_hypotheses(self, design):
        for rq in ResearchQuestion:
            assert rq in design.hypotheses

    def test_each_rq_has_null_and_alternative(self, design):
        for rq in ResearchQuestion:
            h0, h1 = design.get_hypotheses(rq)
            assert h0.type == HypothesisType.NULL
            assert h1.type == HypothesisType.ALTERNATIVE

    def test_hypotheses_belong_to_correct_rq(self, design):
        for rq in ResearchQuestion:
            h0, h1 = design.get_hypotheses(rq)
            assert h0.rq == rq
            assert h1.rq == rq

    def test_hypotheses_have_non_empty_statements(self, design):
        for rq in ResearchQuestion:
            h0, h1 = design.get_hypotheses(rq)
            assert h0.statement
            assert h1.statement


class TestVariables:
    def test_independent_variable_is_ai_usage(self, design):
        assert design.independent_variable.type == VariableType.INDEPENDENT

    def test_has_dependent_variables_for_all_rqs(self, design):
        rqs_covered = {
            rq
            for var in design.dependent_variables
            for rq in var.research_questions
        }
        assert ResearchQuestion.RQ1 in rqs_covered
        assert ResearchQuestion.RQ2 in rqs_covered
        assert ResearchQuestion.RQ3 in rqs_covered

    def test_has_loc_as_control_variable(self, design):
        control_names = [v.name for v in design.control_variables]
        assert any("LOC" in name for name in control_names)


class TestProtocol:
    def test_correct_number_of_participants_and_katas(self, design):
        assert design.protocol.participants == PARTICIPANTS
        assert design.protocol.n_katas == N_KATAS
        assert design.protocol.time_box_minutes == TIME_BOX_MINUTES

    def test_each_participant_does_all_katas(self, design):
        for participant in PARTICIPANTS:
            assignments = design.protocol.get_assignments_for_participant(participant)
            assert len(assignments) == N_KATAS

    def test_each_participant_does_equal_trials_per_treatment(self, design):
        for participant in PARTICIPANTS:
            assignments = design.protocol.get_assignments_for_participant(participant)
            with_ai = sum(1 for a in assignments if a.treatment == Treatment.WITH_AI)
            without_ai = sum(1 for a in assignments if a.treatment == Treatment.WITHOUT_AI)
            assert with_ai == without_ai == N_KATAS // 2

    def test_each_kata_covered_by_both_treatments_across_participants(self, design):
        for kata_idx in range(N_KATAS):
            assignments = design.protocol.get_assignments_for_kata(kata_idx)
            treatments = {a.treatment for a in assignments}
            assert Treatment.WITH_AI in treatments
            assert Treatment.WITHOUT_AI in treatments

    def test_get_treatment_returns_correct_value(self, design):
        protocol = design.protocol
        for participant in PARTICIPANTS:
            for kata_idx in range(N_KATAS):
                treatment = protocol.get_treatment(participant, kata_idx)
                assert isinstance(treatment, Treatment)

    def test_get_treatment_raises_for_invalid_participant(self, design):
        with pytest.raises(ValueError):
            design.protocol.get_treatment("Unknown", 0)


class TestThreats:
    def test_has_internal_validity_threats(self, design):
        categories = {t.category for t in design.threats}
        assert ThreatCategory.INTERNAL_VALIDITY in categories

    def test_has_statistical_conclusion_threat(self, design):
        categories = {t.category for t in design.threats}
        assert ThreatCategory.STATISTICAL_CONCLUSION in categories

    def test_has_external_validity_threat(self, design):
        categories = {t.category for t in design.threats}
        assert ThreatCategory.EXTERNAL_VALIDITY in categories

    def test_all_threats_have_mitigation(self, design):
        for threat in design.threats:
            assert threat.mitigation


class TestExperimentDesignBuilder:
    def test_build_raises_without_goal(self):
        from experiment.config.experiment_design_builder import ExperimentDesignBuilder
        from experiment.config.counterbalancing import BlockCounterbalancingStrategy
        from experiment.domain.enums import VariableType
        from experiment.domain.variable import Variable

        builder = (
            ExperimentDesignBuilder()
            .with_independent_variable(
                Variable("X", "desc", VariableType.INDEPENDENT, "unit", (ResearchQuestion.RQ1,))
            )
            .with_protocol(("P1",), 2, 35, BlockCounterbalancingStrategy())
        )
        with pytest.raises(ValueError, match="objetivo"):
            builder.build()

    def test_add_hypothesis_raises_for_mismatched_rqs(self):
        from experiment.config.experiment_design_builder import ExperimentDesignBuilder
        from experiment.domain.hypothesis import Hypothesis

        builder = ExperimentDesignBuilder()
        with pytest.raises(ValueError):
            builder.add_hypothesis(
                h0=Hypothesis(ResearchQuestion.RQ1, HypothesisType.NULL, "H0"),
                h1=Hypothesis(ResearchQuestion.RQ2, HypothesisType.ALTERNATIVE, "H1"),
            )
