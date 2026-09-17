def rotate_teams(people: list[str], team_size: int) -> list[list[str]]:
    if not people: 
        raise ValueError("A lista de pessoas não pode ser vazia")
    if team_size <= 0:
        raise ValueError("O tamanho da equipe deve ser maior que zero")
    teams = []
    for i in range(0, len(people), team_size):
        teams.append(people[i:i+team_size])
    return [teams[-1]] + teams[:-1]