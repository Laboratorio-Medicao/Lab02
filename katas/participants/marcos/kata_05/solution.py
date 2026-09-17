def rotate_teams(people: list[str], team_size: int) -> list[list[str]]:
    if not people or team_size <= 0:
        raise ValueError("pessoas ou tamanho de equipe inválido")

    teams = [
        people[start:start + team_size]
        for start in range(0, len(people), team_size)
    ]
    return [teams[-1], *teams[:-1]]
