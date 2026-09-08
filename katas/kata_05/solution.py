def rotate_teams(people: list[str], team_size: int) -> list[list[str]]:
    if not people or team_size <= 0:
        raise ValueError("pessoas ou tamanho invalido")
    teams = [people[index:index + team_size] for index in range(0, len(people), team_size)]
    return [teams[-1], *teams[:-1]]