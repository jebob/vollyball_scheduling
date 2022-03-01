"""
Andrew Tatarek asked me to help organize a volleyball tournament. Given a set of groups of teams called ORIGINAL_GROUPS
I need to assign which team will play which when and which team will referee. This is part of a larger solution that
Andrew Tatarek built in Microsoft Excel. The output of this file is a grid where each column is a set of games and
rows repeat: "team1, team2, referee" for each match.

Tries to minimize score =
    Number of games where the referee is from a different group * 0.1
    + (max(games played per team) - min(games played per team)) * 5
    + sum(max(games played per team) - min(games played per team) for each group) * 2
    + sum(max(games played or refereed per team) - min(games played or refereed per team) for each group)

The code in this file was written jointly by Michael Howlett and David Howlett.
"""

import copy
import random
from typing import List

# groups = [
#     ["teamA1", "teamA2", "teamA3", "teamA4", "teamA5"],
#     ["teamB1", "teamB2", "teamB3", "teamB4", "teamB5", "teamB6", "teamB7"],
#     ["teamC1", "teamC2", "teamC3", "teamC4", "teamC5", "teamC6", "teamC7", "teamC8"],
# ]
ORIGINAL_GROUPS = [
    ["Team1-01", "Team1-02", "Team1-03", "Team1-04", "Team1-05"],
    ["Team2-01", "Team2-02", "Team2-03", "Team2-04", "Team2-05"],
    ["Team3-01", "Team3-02", "Team3-03", "Team3-04", "Team3-05"],
    ["Team4-01", "Team4-02", "Team4-03", "Team4-04", "Team4-05", "Team4-06"],
]
NUM_OF_SIMULATION: int = 500  # number of times it tries to produce a setup, higher improves matching but slows program
ROUNDS = 11  # number of rounds of games
NUM_OF_COURTS = 6
COURTS_TO_USE = min(NUM_OF_COURTS, len({team for group in ORIGINAL_GROUPS for team in group}) // 3)
# debugging is easier if the randomness is not really random.
# random.seed(10)


class EmptyCourtException(Exception):
    """thrown when the court is unexpectedly empty"""


class TeamStats:
    def __init__(self, name: str, group: List[str]):
        self.id = name
        playable = group.copy()
        playable.remove(name)
        random.shuffle(playable)
        self.eligible_opponents = playable
        self.previous_opponents = []
        self.games_played = 0
        self.games_refereed = 0
        self.backup_opponents = playable.copy()

    def play(self, other: str):
        if other not in self.eligible_opponents:
            self.eligible_opponents.extend(self.backup_opponents)
        self.eligible_opponents.remove(other)
        self.previous_opponents.append(other)
        self.games_played += 1


def reformat_teams(given_groups):
    """
    replace team with TeamStats object
    """
    new_groups = []
    for group in given_groups:
        new_group = [TeamStats(name=team, group=group) for team in group]
        new_groups.append(new_group)
    return new_groups


def print_table(output_matrix):
    """
    This prints the transpose of the table in the code
    """
    for i in range(COURTS_TO_USE * 3):
        to_output = ""
        for j in range(ROUNDS):
            to_output = to_output + "\t\t" + output_matrix[j][i]
        print(to_output[2:])


def run_sims(groups):
    """
    generate a collection of solutions with a bit of randomness and return the best one,
    the best score and the average score
    """
    best_output_matrix = []
    best_match_up_score = 999999  # This will be overridden later
    average_match_up_score = 0
    for _ in range(NUM_OF_SIMULATION):  # run the setup "NUM_OF_SIMULATION" times and picks best
        # Michael found another bug which crashes the code once every few hundred games.
        # where if for all teams the [teams they can play against] are already playing someone else, no game gets
        # added causing an empty court and a crash. Due to rarity, we just catch the error and continue.
        try:
            match_up_score, output_matrix, result_groups = run_sim(copy.deepcopy(groups))
        except EmptyCourtException:
            continue
        match_up_score = get_score(result_groups, match_up_score)

        if match_up_score < best_match_up_score:
            best_match_up_score = match_up_score
            best_output_matrix = output_matrix
        average_match_up_score += match_up_score / NUM_OF_SIMULATION
    return best_output_matrix, average_match_up_score, best_match_up_score


def run_sim(groups):
    """
    generate a single solution and partially scores it
    """
    output_matrix = []
    # at this point in the calculation the number format of groups is changed
    groups = reformat_teams(groups)
    match_up_score = 0
    for _ in range(ROUNDS):
        courts, occupied = one_court_per_group(groups)
        fill_in_missing_players(courts, groups, occupied)
        match_up_score += add_referees(courts, groups, occupied)
        to_output = []
        for court in courts:
            to_output.extend(court)
        output_matrix.append(to_output)
    return match_up_score, output_matrix, groups


def one_court_per_group(groups: List[List[TeamStats]]):
    """
    This fills in 1 court per group to help balance the number of courts allocated to each group
    """
    courts = [[]] * COURTS_TO_USE
    occupied = []  # teams which are busy.
    for court_id, group in enumerate(groups):
        i, j = 9999, 0
        for k, team in enumerate(group):
            if team.games_played < i:
                i = team.games_played
                j = k
        if not group[j].eligible_opponents:
            group[j].eligible_opponents = group[j].backup_opponents.copy()
        courts[court_id] = [group[j].id, group[j].eligible_opponents[0], court_id]
        # update team information so that the teams don't repeat.
        occupied.append(group[j].id)
        occupied.append(group[j].eligible_opponents[0])
        # update team 2 info
        for team in group:
            if team.id == group[j].eligible_opponents[0]:
                team.play(group[j].id)
        # update team 1 info
        group[j].play(group[j].eligible_opponents[0])
    return courts, occupied


def fill_in_missing_players(courts, groups, occupied):
    """
    fills in players for the remaining courts with some randomness
    """
    for court_id, court in enumerate(courts):
        if court:
            # Court already filled
            continue
        # find team with the least games
        least = min(team.games_played for group in groups for team in group)
        escape = False
        for i in range(200):  # pick a group at random upto 100 times to find an available team.
            if escape:  # need to break out of 3 while loops, so this is how I did it.
                break
            if i == 100:
                least += 1
            group_no = random.randint(0, len(groups) - 1)
            group = groups[group_no]
            escape = False
            for team in group:
                if escape:
                    break
                if team.id in occupied:  # the team is already playing
                    continue
                if team.games_played == least:  # if no team has played less than this one
                    if not team.eligible_opponents:
                        team.eligible_opponents = team.backup_opponents.copy()
                    for team2 in group:
                        if team2.id in team.eligible_opponents:
                            if team2.id not in occupied:
                                # a game shall be played between team2 and team 1
                                courts[court_id] = [
                                    team.id,
                                    team2.id,
                                    group_no,
                                ]
                                if team.id not in team2.eligible_opponents:
                                    team2.eligible_opponents = team2.backup_opponents.copy()
                                occupied.append(team2.id)
                                occupied.append(team.id)
                                team.play(team2.id)
                                team2.play(team.id)
                                escape = True
                                break


def add_referees(courts, groups, occupied):
    """
    Add referees to all the matches
    """
    match_up_score = 0  # how bad the setup of matches is
    for court in courts:
        if not court:
            raise EmptyCourtException
        group = groups[court[2]]
        found = False
        min_refs = 9999  # minimum number of games refereed by a team in the group
        best_team = 9999  # team with the least referees
        for i, team in enumerate(group):  # try to find a ref from the same group
            if team.id not in occupied:
                if team.games_refereed <= min_refs:
                    min_refs = team.games_refereed
                    best_team = i
                    found = True
        if found:
            occupied.append(group[best_team].id)
            court[2] = group[best_team].id
            group[best_team].games_refereed += 1
        else:  # find one from a different group
            match_up_score += 0.1
            for _ in range(100):
                group = groups[random.randint(0, len(groups) - 1)]
                for i, team in enumerate(group):  # try to find a ref from the same group
                    if team.id not in occupied:
                        if team.games_refereed <= min_refs:
                            min_refs = team.games_refereed
                            best_team = i
                            found = True
                if found:
                    occupied.append(group[best_team].id)
                    court[2] = group[best_team].id
                    group[best_team].games_refereed += 1
                    break
    return match_up_score


def get_score(groups, match_up_score):
    """
    given a partially calculated score, and the datastructure describing the solution,
    calculate the final score
    """
    min_games = 9999
    max_games = 0
    for group in groups:
        min_g = 9999  # min games within the group
        max_g = 0
        min_used = 9999  # minimum number of times a group is either referee or playing
        max_used = 0
        for team in group:
            # I would do "min_games = min(min_games,team.games_played)", but couldn't get it to work
            if min_games > team.games_played:
                min_games = team.games_played
            if max_games < team.games_played:
                max_games = team.games_played
            if min_g > team.games_played:
                min_g = team.games_played
            if max_g < team.games_played:
                max_g = team.games_played
            if min_used > team.games_played + team.games_refereed:
                min_used = team.games_played + team.games_refereed
            if max_used < team.games_played + team.games_refereed:
                max_used = team.games_played + team.games_refereed
        match_up_score += (max_g - min_g) * 2 + (max_used - min_used)
    match_up_score += (max_games - min_games) * 5
    # print(match_up_score)
    return match_up_score


def main():
    """
    Run the simulation and print the results
    """
    best_output_matrix, average_match_up_score, best_match_up_score = run_sims(ORIGINAL_GROUPS)
    print_table(best_output_matrix)
    print(
        best_match_up_score,
        "best score compared to average of :",
        average_match_up_score,
    )


if __name__ == "__main__":
    main()
