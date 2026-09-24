# Desenho do Experimento — Lab02

## Objetivo (GQM)

Analisar o uso de assistentes de IA generativa na resolução de tarefas de programação, com o propósito de comparar seu efeito frente à codificação manual, com respeito a tempo de resolução, qualidade funcional (defeitos) e qualidade estrutural do código produzido, do ponto de vista do grupo pesquisador, no contexto de katas de dificuldade equivalente resolvidos por estudantes de graduação sob condições controladas (crossover within-subject, time-boxed).

## Hipóteses

### RQ1

- **H0:** O uso de assistente de IA não reduz o tempo necessário para resolver uma tarefa de programação.
- **H1:** O uso de assistente de IA reduz o tempo necessário para resolver uma tarefa de programação.

### RQ2

- **H0:** O uso de assistente de IA não reduz a quantidade de defeitos (testes que falham) no código produzido.
- **H1:** O uso de assistente de IA reduz a quantidade de defeitos (testes que falham) no código produzido.

### RQ3

- **H0:** O uso de assistente de IA não altera a complexidade ciclomática nem a duplicação do código produzido.
- **H1:** O uso de assistente de IA altera a complexidade ciclomática e/ou a duplicação do código produzido.

## Variáveis

**Variável independente:** Uso de assistente de IA — Presença ou ausência de assistente de IA generativa durante a resolução do kata.

**Variáveis dependentes:**

- **Tempo até green (time-to-green)** (segundos) — Tempo decorrido desde o início do trial até todos os testes de aceitação passarem. Trials que atingem o time-box sem sucesso são registrados como censurados em 35 min. `[RQ1]`
- **Taxa de sucesso** (%) — Percentual de testes de aceitação passando ao final do time-box. Normaliza katas com números diferentes de testes. `[RQ2]`
- **Número de testes falhando** (inteiro) — Contagem absoluta de testes de aceitação falhando ao final do time-box. `[RQ2]`
- **Complexidade ciclomática média (CC)** (adimensional) — Complexidade ciclomática média por método/função via Radon cc. `[RQ3]`
- **Índice de Manutenibilidade (MI)** (0–100) — Métrica composta via Radon mi: combina complexidade ciclomática, LOC e volume de Halstead. Escala 0–100. Métrica opcional de aprofundamento (linha 55 do enunciado): o grupo optou por incluí-la porque combina CC, LOC e volume de Halstead em um único índice, permitindo comparar a manutenibilidade geral do código com e sem IA de forma mais robusta do que olhar CC e duplicação isoladamente. `[RQ3]`
- **Duplicação de código** (%) — Percentual de linhas duplicadas via jscpd. `[RQ3]`

	A coleta usa jscpd (versão efetivamente instalada, reportada em `duplication_tool_version` a cada execução — ver `experiment/collection/duplication_metrics.py`), considera os arquivos Python do diretório do trial e aplica limiar mínimo de 5 linhas e 20 tokens para reconhecer um bloco duplicado. Arquivos `test_*.py` e `*_test.py` são excluídos; o diretório do trial deve conter somente o código produzido pelo participante.

**Variáveis de controle:**

- **LOC (linhas de código)** (linhas) — Total de linhas de código. Usado para normalizar complexidade e duplicação — código gerado com IA pode ser mais verboso. `[RQ3]`

## Protocolo Experimental

- **Tipo:** Crossover within-subject contrabalanceado
- **Participantes:** Guilherme, Arthur, Marcos
- **Katas:** 6
- **Time-box por trial:** 35 min
- **Medições totais:** 18 trials (6 katas × 3 participantes)

Os objetos experimentais são os 6 exercícios autorais documentados em [`docs/katas.md`](katas.md): Faixas de sinal, Inventário de bolsos, Grade de entregas, Marcadores de texto, Rodízio de equipes e Pontuação por vizinhança. Cada um possui testes automatizados de aceitação em [`katas/`](../katas/).

### Atribuição de tratamentos

| Participante | Kata | Tratamento |
|---|---|---|
| Guilherme | kata-01 a kata-03 | Com IA |
| Guilherme | kata-04 a kata-06 | Sem IA |
| Arthur | kata-01, kata-03 e kata-05 | Com IA |
| Arthur | kata-02, kata-04 e kata-06 | Sem IA |
| Marcos | kata-01 a kata-03 | Sem IA |
| Marcos | kata-04 a kata-06 | Com IA |

<!-- manual:start protocolo -->
### Registro de desvio de protocolo (adicionado em 2026-09-17)

A tabela acima é a atribuição **efetivamente executada** na S02. Ela difere
da atribuição originalmente fechada no desenho da S01 (Issue #3, commit
`906bafc`, 2026-09-06), que era:

> **Nota sobre hashes (2026-09-24):** o histórico de `main` foi reescrito após a
> S03. Os hashes citados neste documento são os do histórico atual de `main`;
> os hashes originais (ex.: `e9478c3`, `c826baa`, `805bb72`) só existem nas
> branches `feature/*` do repositório remoto.

| Participante | Kata | Tratamento original (S01) |
|---|---|---|
| Guilherme | kata-01 a kata-03 | Com IA *(sem alteração)* |
| Guilherme | kata-04 a kata-06 | Sem IA *(sem alteração)* |
| Arthur | kata-01 a kata-03 | Sem IA *(alterado — ver abaixo)* |
| Arthur | kata-04 a kata-06 | Com IA *(alterado — ver abaixo)* |
| Marcos | kata-01 a kata-03 | Com IA *(alterado — ver abaixo)* |
| Marcos | kata-04 a kata-06 | Sem IA *(alterado — ver abaixo)* |

**O que mudou:**
- **Arthur** passou de atribuição em bloco (katas 1–3 sem IA / 4–6 com IA)
  para atribuição alternada (katas 1, 3, 5 com IA / 2, 4, 6 sem IA). A
  mudança foi commitada junto com os dados de Arthur (commit `07398a7`,
  2026-09-17).
- **Marcos** teve o bloco invertido (de "1–3 com IA / 4–6 sem IA" para "1–3
  sem IA / 4–6 com IA"). A mudança foi commitada junto com os dados de Marcos
  (commit `c30be82`, 2026-09-16); o corpo da Issue #11 já refletia a nova
  ordem desde 2026-09-15.
- **Guilherme** não teve sua atribuição alterada.

**Motivo do desvio (registrado em 2026-09-17):** segundo relato de Marcos
nesta data, a ordem de tratamentos fechada na S01 se mostrou inviável na
prática durante a execução dos trials, o que levou à mudança de ordem de
Arthur (de bloco para alternada) e de Marcos (bloco invertido). **Ressalva
de rastreabilidade:** este relato foi prestado por Marcos, em nome dos dois,
nesta conversa — não há, até o momento, uma confirmação independente e por
escrito do próprio Arthur sobre o motivo específico de sua mudança de ordem,
nem detalhamento de qual inviabilidade prática foi encontrada por cada um.
Recomenda-se que o Relatório Final traga essa explicação detalhada
diretamente na voz de Arthur e de Marcos (o que, especificamente, tornou a
ordem original inviável — ex.: disponibilidade de horário para os trials,
ordem que não era mais compatível com a agenda de cada um, ou outro fator
concreto), em vez de manter apenas esta descrição genérica de segunda mão.

**Por que isso é registrado:** o desenho crossover contrabalanceado depende
de a ordem de tratamentos ser definida *antes* da execução, para que a
comparação entre participantes não seja enviesada por decisões tomadas
durante a coleta. A ordem final ainda varia entre os três participantes
(o que atende à recomendação de contrabalanceamento), mas o desvio em
relação ao que foi fechado na S01 precisa constar explicitamente no
Relatório Final como uma ameaça adicional à validade interna, já que não é
possível reconstruir, com os artefatos disponíveis, se a mudança ocorreu
antes ou depois da execução real dos trials de cada participante.

### Confirmação de execução — trials "com IA" de Marcos (autorrelato, 2026-09-17)

Os três trials "com IA" de Marcos (kata-04, kata-05, kata-06) têm tempos
muito próximos entre si (36,781 s / 36,824 s / 36,757 s — variação menor que
0,1 s), o que a auditoria de 2026-09-17 registrou como uma anomalia a
confirmar (nenhum log ou timestamp de início de trial existe para verificar
independentemente). Marcos confirmou, em conversa registrada nesta data, que:

- Os três trials foram de fato executados com o assistente de IA (não houve
  qualquer forma de simulação ou preenchimento indireto do tempo).
- O mesmo assistente de IA foi usado nos três — consistente com o ambiente
  fixado em [`README.md`](../README.md) (Claude Code, modelo Claude Sonnet 5).
- O procedimento seguido foi o mesmo nos três trials, o que é a explicação
  dada para a proximidade dos tempos: dado o tamanho pequeno dos katas e um
  fluxo de trabalho repetível com o assistente, o tempo até o "green" variou
  pouco de um kata para o outro.

Esta confirmação é um autorrelato de Marcos, não uma verificação por log
independente (não existe log de sessão do assistente nem timestamp de início
de trial no repositório) — é registrada aqui com essa ressalva, para
complementar (não substituir) a ameaça "Familiaridade prévia com o assistente
de IA" e a observação de anomalia estatística já levantada pela auditoria.

### Justificativa do modelo de Issues por participante (adicionado em 2026-09-17)

O enunciado do LAB02 pede que os trials sejam registrados "como Issues
individuais (uma por kata/tratamento)". O grupo optou, para a S02, por um
modelo diferente: uma Issue por participante (#9 — Guilherme, #10 — Arthur,
#11 — Marcos), cada uma cobrindo os 6 katas desse participante em uma tabela
de atribuição de tratamentos dentro do próprio corpo da Issue (ver seção
"Atribuição de tratamentos" acima, replicada em cada Issue). Um modelo
anterior, com uma Issue por kata por participante (Issues #28–#33), foi
testado e depois explicitamente descartado ("Substituída — voltando ao
design original: cada integrante faz todos os katas.").

**Justificativa da escolha pelo modelo agregado:**

- Cada trial individual (kata × participante × tratamento) continua
  rastreável — a tabela dentro da Issue do participante identifica o
  tratamento de cada um dos 6 katas, e os commits que registram os dados
  (`07398a7`, `c30be82`, `27fcebf`/`3d6cae6`/`66ae97f`/`05574dd`/`8684477`) referenciam
  a Issue correspondente, mantendo a regra de "commit deve referenciar a
  Issue" do enunciado.
- A execução da S02 é, por desenho, organizada por participante: cada
  integrante resolve os 6 katas em sequência, sob o mesmo time-box e o mesmo
  protocolo — a granularidade de acompanhamento no Kanban que reflete esse
  fluxo real de trabalho é "uma pessoa resolvendo seus 6 trials", não "um
  card por combinação kata/tratamento" isolada.
- O modelo por kata/participante (Issues #28–#33) foi tentado primeiro e
  descartado por gerar mais sobrecarga de gestão do quadro (18 cards
  possíveis) sem adicionar rastreabilidade que a tabela dentro da Issue
  agregada já não oferecesse.

Esta nota documenta a decisão deliberada do grupo; não é uma reinterpretação
do enunciado — a leitura literal ("uma Issue por kata/tratamento") continua
divergente do modelo adotado, e isso deve ser declarado como tal no Relatório
Final, com esta justificativa como a razão da escolha.
<!-- manual:end protocolo -->

## Ameaças à Validade

### Efeito de aprendizado `[Validade Interna]`

**Descrição:** O participante melhora ao longo dos trials independentemente do tratamento, apenas pela prática repetida.

**Mitigação:** Design crossover contrabalanceado: a ordem dos tratamentos é alternada entre participantes, distribuindo o efeito igualmente.

<!-- manual:start ameaca:efeito-de-aprendizado -->
<!-- manual:end ameaca:efeito-de-aprendizado -->

### Familiaridade prévia com o assistente de IA `[Validade Interna]`

**Descrição:** Participantes com mais experiência com ferramentas de IA podem obter ganhos maiores no tratamento WITH_AI, introduzindo viés.

**Mitigação:** Registrar nível de familiaridade prévia de cada participante em [`data/participant_ai_familiarity.csv`](../data/participant_ai_familiarity.csv) e tratar como variável de confusão na discussão qualitativa.

<!-- manual:start ameaca:familiaridade-previa-com-o-assistente-de-ia -->
**Status da mitigação (atualizado em 2026-09-17):** [`data/participant_ai_familiarity.csv`](../data/participant_ai_familiarity.csv) está preenchido — todos os três relatam uso de assistentes de IA em estágio profissional (familiaridade "Intermediária" para Guilherme e Arthur, "Avançada" para Marcos, por autoavaliação relativa dentro do trio). **Ressalva:** este autorrelato foi coletado por Marcos em nome do grupo. Marcos reconfirmou nesta mesma data o nível de Arthur — mas essa reconfirmação continua sendo prestada por Marcos, não é uma autodeclaração direta e por escrito do próprio Arthur. Guilherme ainda não confirmou individualmente e por escrito seu próprio nível. O CSV registra essa origem no campo `notes` de cada linha. Recomenda-se a confirmação individual e por escrito de Guilherme (e, idealmente, também de Arthur diretamente) antes do Relatório Final, para que a autodeclaração não dependa só do relato de um colega.
<!-- manual:end ameaca:familiaridade-previa-com-o-assistente-de-ia -->

### Memorização pelo assistente de IA `[Validade Interna]`

**Descrição:** Em katas muito conhecidos, o assistente de IA pode reproduzir uma solução memorizada do seu próprio treinamento em vez de efetivamente auxiliar na resolução, inflando artificialmente o desempenho do tratamento WITH_AI.

**Mitigação:** Selecionar katas de baixa indexação, preferencialmente autorais ou pouco divulgados, evitando exercícios clássicos do LeetCode/HackerRank.

<!-- manual:start ameaca:memorizacao-pelo-assistente-de-ia -->
<!-- manual:end ameaca:memorizacao-pelo-assistente-de-ia -->

### Vazamento de solução já vista entre participantes `[Validade Interna]`

**Descrição:** Como os três participantes resolvem os mesmos seis katas no repositório compartilhado do grupo, um participante pode ver a solução de um kata já resolvido por um colega (commit, histórico do Git, conversa) antes do seu próprio trial daquele kata, contaminando a comparação entre tratamentos independentemente do uso de IA.

**Mitigação:** Evitar consultar ou discutir o código de um kata já resolvido por outro participante antes de concluir o próprio trial daquele kata; considerar isolar a solução de cada trial (branch ou diretório próprio) até que todos os participantes tenham resolvido o kata.

<!-- manual:start ameaca:vazamento-de-solucao-ja-vista-entre-participantes -->
**Status observado (registrado em 2026-09-24):** as soluções de referência completas dos seis katas (`katas/kata_0N/solution.py`) foram commitadas no repositório compartilhado em 2026-09-07 (commit `6f79179`, Issue #4, commit feito por Arthur), antes de qualquer trial — os dados e soluções dos trials foram commitados entre 2026-09-16 e 2026-09-17. Os artefatos comprovam que essas soluções **estavam disponíveis** no repositório durante a S02; eles **não** comprovam se algum participante as **acessou**, nem se alguém as **usou**. Também não há registro de como a implementação de referência foi removida antes de cada trial (procedimento previsto em [`docs/katas.md`](katas.md)) nem de quem escreveu as soluções de referência — o git registra apenas quem fez o commit, e esse integrante também foi participante. A mitigação prevista acima (isolamento por diretório entre participantes) não cobre esse caso, porque a referência ficou fora de `katas/participants/`. A ameaça permanece **não mitigada e não mensurável** com os dados disponíveis.
<!-- manual:end ameaca:vazamento-de-solucao-ja-vista-entre-participantes -->

### Tamanho amostral reduzido `[Conclusão Estatística]`

**Descrição:** Com 3 participantes e 6 katas, o poder estatístico é limitado, aumentando o risco de falsos negativos.

**Mitigação:** Usar mediana e IQR em vez de média/desvio-padrão; aplicar teste de Wilcoxon não-paramétrico (within-subject); interpretar os resultados com cautela quanto à generalização.

<!-- manual:start ameaca:tamanho-amostral-reduzido -->
<!-- manual:end ameaca:tamanho-amostral-reduzido -->

### Generalização limitada `[Validade Externa]`

**Descrição:** Os resultados podem não se generalizar para profissionais experientes, outras linguagens, ou contextos de desenvolvimento de produção.

**Mitigação:** Declarar explicitamente o escopo: estudantes de graduação, Python, katas de complexidade equivalente, assistente de IA específico.

<!-- manual:start ameaca:generalizacao-limitada -->
<!-- manual:end ameaca:generalizacao-limitada -->

<!-- manual:start ameacas-adicionais -->
### Desvio de protocolo de contrabalanceamento `[Validade Interna]` (adicionado em 2026-09-17)

**Descrição:** A ordem de tratamentos efetivamente executada por Arthur e por Marcos diverge da ordem fechada no desenho original da S01 (ver "Registro de desvio de protocolo" acima). Não há, nos artefatos do projeto, registro do motivo da mudança nem confirmação de que ela foi decidida antes da execução dos trials — o que introduz um risco à validade interna: não é possível descartar, com os dados disponíveis, que a ordem tenha sido ajustada a posteriori para coincidir com o que já havia sido executado.

**Mitigação:** Nenhuma mitigação foi aplicada no momento da mudança (o desvio não foi documentado quando ocorreu). Mitigação corretiva: Arthur e Marcos devem registrar, no Relatório Final, o motivo real da mudança e, se possível, evidência independente de quando cada trial foi de fato executado (ex.: histórico do editor, timestamps de arquivos locais antes do commit), para permitir avaliar se o desvio compromete a comparabilidade dos resultados desses dois participantes.
<!-- manual:end ameacas-adicionais -->
