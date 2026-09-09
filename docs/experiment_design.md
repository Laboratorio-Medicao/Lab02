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

	A coleta usa jscpd (versão efetivamente instalada, reportada em `tool_version` a cada execução — ver `experiment/collection/duplication_metrics.py`), considera os arquivos Python do diretório do trial e aplica limiar mínimo de 5 linhas e 20 tokens para reconhecer um bloco duplicado. Arquivos `test_*.py` e `*_test.py` são excluídos; o diretório do trial deve conter somente o código produzido pelo participante.

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
| Arthur | kata-01 a kata-03 | Sem IA |
| Arthur | kata-04 a kata-06 | Com IA |
| Marcos | kata-01 a kata-03 | Com IA |
| Marcos | kata-04 a kata-06 | Sem IA |

## Ameaças à Validade

### Efeito de aprendizado `[Validade Interna]`

**Descrição:** O participante melhora ao longo dos trials independentemente do tratamento, apenas pela prática repetida.

**Mitigação:** Design crossover contrabalanceado: a ordem dos tratamentos é alternada entre participantes, distribuindo o efeito igualmente.

### Familiaridade prévia com o assistente de IA `[Validade Interna]`

**Descrição:** Participantes com mais experiência com ferramentas de IA podem obter ganhos maiores no tratamento WITH_AI, introduzindo viés.

**Mitigação:** Registrar nível de familiaridade prévia de cada participante e tratar como variável de confusão na discussão qualitativa.

### Memorização pelo assistente de IA `[Validade Interna]`

**Descrição:** Em katas muito conhecidos, o assistente de IA pode reproduzir uma solução memorizada do seu próprio treinamento em vez de efetivamente auxiliar na resolução, inflando artificialmente o desempenho do tratamento WITH_AI.

**Mitigação:** Selecionar katas de baixa indexação, preferencialmente autorais ou pouco divulgados, evitando exercícios clássicos do LeetCode/HackerRank.

### Vazamento de solução já vista entre participantes `[Validade Interna]`

**Descrição:** Como os três participantes resolvem os mesmos seis katas no repositório compartilhado do grupo, um participante pode ver a solução de um kata já resolvido por um colega (commit, histórico do Git, conversa) antes do seu próprio trial daquele kata, contaminando a comparação entre tratamentos independentemente do uso de IA.

**Mitigação:** Evitar consultar ou discutir o código de um kata já resolvido por outro participante antes de concluir o próprio trial daquele kata; considerar isolar a solução de cada trial (branch ou diretório próprio) até que todos os participantes tenham resolvido o kata.

### Tamanho amostral reduzido `[Conclusão Estatística]`

**Descrição:** Com 3 participantes e 6 katas, o poder estatístico é limitado, aumentando o risco de falsos negativos.

**Mitigação:** Usar mediana e IQR em vez de média/desvio-padrão; aplicar teste de Wilcoxon não-paramétrico (within-subject); interpretar os resultados com cautela quanto à generalização.

### Generalização limitada `[Validade Externa]`

**Descrição:** Os resultados podem não se generalizar para profissionais experientes, outras linguagens, ou contextos de desenvolvimento de produção.

**Mitigação:** Declarar explicitamente o escopo: estudantes de graduação, Python, katas de complexidade equivalente, assistente de IA específico.
