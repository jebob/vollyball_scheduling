"""
Code to attempt to find the best setup of matches for playing volly ball, with 1 team per side and 1 team as ref
Input is a list of lists of team names. Each outer list is a group. Don't repeat team names.
Output is a grid where each column is a set of games and rows repeat: "team1, team2, referee" for a match.

A solution is a list of rounds
A round is a list of matches
A match is a tuple of referee, left side player and right side player
"""

import random
from typing import List, Tuple

ROUNDS = 11  # number of rounds of the tournament
NUM_OF_COURTS = 6
TEAMS_PER_MATCH = 3
groups = [
    ["Team1-01", "Team1-02", "Team1-03", "Team1-04", "Team1-05", "Team1-06"],
    ["Team2-01", "Team2-02", "Team2-03", "Team2-04", "Team2-05"],
    ["Team3-01", "Team3-02", "Team3-03", "Team3-04", "Team3-05"],
    ["Team4-01", "Team4-02", "Team4-03", "Team4-04", "Team4-05", "Team4-06"],
]

# How bad is it for a team to do more than one thing in a round?
DUPLICATED_TEAMS_WEIGHT = 999


def starting_solution() -> List[List[Tuple[str, str, str]]]:
    """Creates an initial solution to iterate on"""
    all_teams: List[str] = sum(groups, [])
    solution = []
    for _ in range(ROUNDS):
        column = []
        for _ in range(NUM_OF_COURTS):
            match = tuple(random.choices(all_teams, k=3))
            column.append(match)
        solution.append(column)
    return solution  # type: ignore


def get_score(solution: List[List[Tuple[str, str, str]]]) -> int:
    """
    Assigns a numerical score to a solution
    """

    score = 0
    # Within each round a team can do at most one thing also every match must have a complete set of
    # (left team, right team, ref) These two score modifications can be calculated at the same time by adding a None
    # then looking for duplicates
    for round in solution:
        count_of_teams = len({team for match in round for team in match}.union({None})) - 1
        score += DUPLICATED_TEAMS_WEIGHT * (NUM_OF_COURTS * TEAMS_PER_MATCH - count_of_teams)

    # Teams can only play teams from within their group
    # - 999 *(number of matches between different groups)

    # Close to equal number of match ups within a group
    # 10*(max(games played in a group)-min(games played in a group)) summed over all groups

    # Maximise the gaps between repeat matchups
    # -10/(time of second match - time of first match) summed for all pairs of repeats

    # Similar number of breaks (when a team is not playing or reffing) or total on court
    # -(5*(number of breaks for the team)**1.5) summed for all teams

    # Refereering preferably within the group
    # -1*(number of time refereeing happens across groups)

    score = 5
    return score


def print_table(solution):
    """returns a 2d table for a solution that can be pasted into excel"""
    for court in range(NUM_OF_COURTS):
        print("\t\t".join(round[court][0] for round in solution))
        print("\t\t".join(round[court][1] for round in solution))
        print("\t\t".join(round[court][2] for round in solution))
    print(f"score: {get_score(solution)}")


def main():
    initial_solution = starting_solution()

    print("Initial solution:")
    print_table(initial_solution)

    print("\nFinal solution:")
    print_table(initial_solution)


if __name__ == "__main__":
    main()
