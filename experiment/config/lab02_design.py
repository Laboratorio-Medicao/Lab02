from experiment.config.counterbalancing import BlockCounterbalancingStrategy
from experiment.config.experiment_design import ExperimentDesign
from experiment.config.experiment_design_builder import ExperimentDesignBuilder
from experiment.domain.enums import (
    HypothesisType,
    ResearchQuestion,
    ThreatCategory,
    VariableType,
)
from experiment.domain.hypothesis import Hypothesis
from experiment.domain.threat import Threat
from experiment.domain.variable import Variable

PARTICIPANTS = ("Guilherme", "Arthur", "Marcos")
N_KATAS = 6
TIME_BOX_MINUTES = 35


def create_lab02_design() -> ExperimentDesign:
    return (
        ExperimentDesignBuilder()
        .with_goal(
            "Analisar o uso de assistentes de IA generativa na resolução de tarefas de "
            "programação, com o propósito de comparar seu efeito frente à codificação "
            "manual, com respeito a tempo de resolução, qualidade funcional (defeitos) e "
            "qualidade estrutural do código produzido, do ponto de vista do grupo "
            "pesquisador, no contexto de katas de dificuldade equivalente resolvidos por "
            "estudantes de graduação sob condições controladas (crossover within-subject, "
            "time-boxed)."
        )
        .add_hypothesis(
            h0=Hypothesis(
                rq=ResearchQuestion.RQ1,
                type=HypothesisType.NULL,
                statement=(
                    "O uso de assistente de IA não reduz o tempo necessário para "
                    "resolver uma tarefa de programação."
                ),
            ),
            h1=Hypothesis(
                rq=ResearchQuestion.RQ1,
                type=HypothesisType.ALTERNATIVE,
                statement=(
                    "O uso de assistente de IA reduz o tempo necessário para "
                    "resolver uma tarefa de programação."
                ),
            ),
        )
        .add_hypothesis(
            h0=Hypothesis(
                rq=ResearchQuestion.RQ2,
                type=HypothesisType.NULL,
                statement=(
                    "O uso de assistente de IA não reduz a quantidade de defeitos "
                    "(testes que falham) no código produzido."
                ),
            ),
            h1=Hypothesis(
                rq=ResearchQuestion.RQ2,
                type=HypothesisType.ALTERNATIVE,
                statement=(
                    "O uso de assistente de IA reduz a quantidade de defeitos "
                    "(testes que falham) no código produzido."
                ),
            ),
        )
        .add_hypothesis(
            h0=Hypothesis(
                rq=ResearchQuestion.RQ3,
                type=HypothesisType.NULL,
                statement=(
                    "O uso de assistente de IA não altera a complexidade ciclomática "
                    "nem a duplicação do código produzido."
                ),
            ),
            h1=Hypothesis(
                rq=ResearchQuestion.RQ3,
                type=HypothesisType.ALTERNATIVE,
                statement=(
                    "O uso de assistente de IA altera a complexidade ciclomática "
                    "e/ou a duplicação do código produzido."
                ),
            ),
        )
        .with_independent_variable(
            Variable(
                name="Uso de assistente de IA",
                description=(
                    "Presença ou ausência de assistente de IA generativa durante a "
                    "resolução do kata."
                ),
                type=VariableType.INDEPENDENT,
                unit="binário (WITH_AI / WITHOUT_AI)",
                research_questions=(
                    ResearchQuestion.RQ1,
                    ResearchQuestion.RQ2,
                    ResearchQuestion.RQ3,
                ),
            )
        )
        .add_dependent_variable(
            Variable(
                name="Tempo até green (time-to-green)",
                description=(
                    "Tempo decorrido desde o início do trial até todos os testes de "
                    "aceitação passarem. Trials que atingem o time-box sem sucesso são "
                    "registrados como censurados em 35 min."
                ),
                type=VariableType.DEPENDENT,
                unit="segundos",
                research_questions=(ResearchQuestion.RQ1,),
            )
        )
        .add_dependent_variable(
            Variable(
                name="Taxa de sucesso",
                description=(
                    "Percentual de testes de aceitação passando ao final do time-box. "
                    "Normaliza katas com números diferentes de testes."
                ),
                type=VariableType.DEPENDENT,
                unit="%",
                research_questions=(ResearchQuestion.RQ2,),
            )
        )
        .add_dependent_variable(
            Variable(
                name="Número de testes falhando",
                description="Contagem absoluta de testes de aceitação falhando ao final do time-box.",
                type=VariableType.DEPENDENT,
                unit="inteiro",
                research_questions=(ResearchQuestion.RQ2,),
            )
        )
        .add_dependent_variable(
            Variable(
                name="Complexidade ciclomática média (CC)",
                description="Complexidade ciclomática média por método/função via Radon cc.",
                type=VariableType.DEPENDENT,
                unit="adimensional",
                research_questions=(ResearchQuestion.RQ3,),
            )
        )
        .add_dependent_variable(
            Variable(
                name="Índice de Manutenibilidade (MI)",
                description=(
                    "Métrica composta via Radon mi: combina complexidade ciclomática, "
                    "LOC e volume de Halstead. Escala 0–100."
                ),
                type=VariableType.DEPENDENT,
                unit="0–100",
                research_questions=(ResearchQuestion.RQ3,),
            )
        )
        .add_dependent_variable(
            Variable(
                name="Duplicação de código",
                description="Percentual de linhas duplicadas via jscpd.",
                type=VariableType.DEPENDENT,
                unit="%",
                research_questions=(ResearchQuestion.RQ3,),
            )
        )
        .add_control_variable(
            Variable(
                name="LOC (linhas de código)",
                description=(
                    "Total de linhas de código. Usado para normalizar complexidade e "
                    "duplicação — código gerado com IA pode ser mais verboso."
                ),
                type=VariableType.CONTROL,
                unit="linhas",
                research_questions=(ResearchQuestion.RQ3,),
            )
        )
        .add_threat(
            Threat(
                category=ThreatCategory.INTERNAL_VALIDITY,
                name="Efeito de aprendizado",
                description=(
                    "O participante melhora ao longo dos trials independentemente do "
                    "tratamento, apenas pela prática repetida."
                ),
                mitigation=(
                    "Design crossover contrabalanceado: a ordem dos tratamentos é "
                    "alternada entre participantes, distribuindo o efeito igualmente."
                ),
            )
        )
        .add_threat(
            Threat(
                category=ThreatCategory.INTERNAL_VALIDITY,
                name="Familiaridade prévia com o assistente de IA",
                description=(
                    "Participantes com mais experiência com ferramentas de IA podem "
                    "obter ganhos maiores no tratamento WITH_AI, introduzindo viés."
                ),
                mitigation=(
                    "Registrar nível de familiaridade prévia de cada participante e "
                    "tratar como variável de confusão na discussão qualitativa."
                ),
            )
        )
        .add_threat(
            Threat(
                category=ThreatCategory.INTERNAL_VALIDITY,
                name="Memorização e vazamento de solução",
                description=(
                    "Em katas muito conhecidos, o assistente de IA pode reproduzir uma "
                    "solução memorizada em vez de efetivamente auxiliar na resolução, "
                    "inflando artificialmente o desempenho do tratamento WITH_AI."
                ),
                mitigation=(
                    "Selecionar katas de baixa indexação, preferencialmente autorais ou "
                    "pouco divulgados, evitando exercícios clássicos do LeetCode/HackerRank."
                ),
            )
        )
        .add_threat(
            Threat(
                category=ThreatCategory.STATISTICAL_CONCLUSION,
                name="Tamanho amostral reduzido",
                description=(
                    "Com 3 participantes e 6 katas, o poder estatístico é limitado, "
                    "aumentando o risco de falsos negativos."
                ),
                mitigation=(
                    "Usar mediana e IQR em vez de média/desvio-padrão; aplicar teste de "
                    "Wilcoxon não-paramétrico (within-subject); interpretar os resultados "
                    "com cautela quanto à generalização."
                ),
            )
        )
        .add_threat(
            Threat(
                category=ThreatCategory.EXTERNAL_VALIDITY,
                name="Generalização limitada",
                description=(
                    "Os resultados podem não se generalizar para profissionais experientes, "
                    "outras linguagens, ou contextos de desenvolvimento de produção."
                ),
                mitigation=(
                    "Declarar explicitamente o escopo: estudantes de graduação, Python, "
                    "katas de complexidade equivalente, assistente de IA específico."
                ),
            )
        )
        .with_protocol(
            participants=PARTICIPANTS,
            n_katas=N_KATAS,
            time_box_minutes=TIME_BOX_MINUTES,
            strategy=BlockCounterbalancingStrategy(),
        )
        .build()
    )
