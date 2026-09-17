def rotate_teams(people: list[str], team_size: int) -> list[list[str]]:
    if not people or team_size <= 0:
        raise ValueError("people must not be empty and team_size must be positive")

    teams = [people[i:i + team_size] for i in range(0, len(people), team_size)]

    if len(teams) <= 1:
        return teams

    return [teams[-1]] + teams[:-1]