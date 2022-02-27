"""
Code to attempt to find the best setup of matches for playing vollyball, with 1 team per side and 1 team as ref
Input is a list of lists of team names, see reference line above. Don't repeat team names.
Output is a grid where each column is a set of games and rows repeat: "team1, team2, referee" for a match.


"""

import copy
import random

# groups = [
#     ["teamA1", "teamA2", "teamA3", "teamA4", "teamA5"],
#     ["teamB1", "teamB2", "teamB3", "teamB4", "teamB5", "teamB6", "teamB7"],
#     ["teamC1", "teamC2", "teamC3", "teamC4", "teamC5", "teamC6", "teamC7", "teamC8"],
# ]
original_groups = [
    ["Team1-01", "Team1-02", "Team1-03", "Team1-04", "Team1-05"],
    ["Team2-01", "Team2-02", "Team2-03", "Team2-04", "Team2-05"],
    ["Team3-01", "Team3-02", "Team3-03", "Team3-04", "Team3-05"],
    ["Team4-01", "Team4-02", "Team4-03", "Team4-04", "Team4-05", "Team4-06"],
]
num_of_simulation = 200  # number of times it tries to produce a setup, higher improves matching but slows program
rounds = 11  # number of rounds of games
num_of_courts = 6
used_courts = min(num_of_courts, len({team for group in original_groups for team in group}) // 3)


def reformat_teams(given_groups):
    """
    replace team with [
        team_name,
        [teams they can play against],
        [teams they already played against],
        total_games_played,
        [backup of teams to play against],
        games refereed
    ]
    """
    new_groups = []
    for group in given_groups:
        new_group = []
        for team in group:
            playable = group.copy()
            playable.remove(team)
            random.shuffle(playable)
            new_group.append([team, playable, [], 0, playable.copy(), 0])
        new_groups.append(new_group)
    return new_groups


def print_table(output_matrix):
    """
    This prints the transpose of the table in the code
    """
    for i in range(used_courts * 3):
        to_output = ""
        for j in range(rounds):
            to_output = to_output + "\t\t" + output_matrix[j][i]
        print(to_output[2:])


def run_sims(groups):
    """
    generate a collection of solutions with a bit of randomness and return the best one,
    the best score and the average score
    """
    global best_output_matrix
    best_output_matrix = []
    best_match_up_score = 999999  # This will be overridden later
    average_match_up_score = 0
    for sim_number in range(num_of_simulation):  # run the setup "num_of_simulation" times and picks best
        match_up_score, output_matrix, result_groups = run_sim(copy.deepcopy(groups))
        match_up_score = get_score(result_groups, match_up_score)

        if match_up_score < best_match_up_score:
            best_match_up_score = match_up_score
            best_output_matrix = output_matrix
        average_match_up_score += match_up_score / num_of_simulation
    return best_output_matrix, average_match_up_score, best_match_up_score


def run_sim(groups):
    """
    generate a single solution and partially scores it
    """
    output_matrix = []
    match_up_score = 0  # how bad the setup of matches is
    # at this point in the calculation the number format of groups is changed
    groups = reformat_teams(groups)
    for round in range(rounds):
        courts = []
        for i in range(used_courts):
            courts.append([])
        # fill in 1 court per group to help balance the numbers
        court_to_fill = -1  # court number being filled
        occupied = []  # teams which are busy.
        for group in groups:
            court_to_fill += 1
            i, j = 9999, 0
            for k in range(len(group)):
                if group[k][3] < i:
                    i = group[k][3]
                    j = k
            if not group[j][1]:
                group[j][1] = group[j][4].copy()
            courts[court_to_fill] = [group[j][0], group[j][1][0], court_to_fill]
            # update team information so that the teams don't repeat.
            occupied.append(group[j][0])
            occupied.append(group[j][1][0])
            # update team 2 info
            for team in group:
                if team[0] == group[j][1][0]:
                    if not team[1]:
                        team[1] = team[4].copy()
                    team[1].remove(group[j][0])
                    team[2].append(group[j][0])
                    team[3] += 1
            # update team 1 info
            group[j][3] = group[j][3] + 1
            group[j][2].append(group[j][1][0])
            group[j][1].pop(0)

        # fills in remaining courts with some randomness
        while court_to_fill < len(courts) - 1:
            court_to_fill += 1
            # find team with the least games
            least = 99999
            for group in groups:
                for team in group:
                    if team[3] < least:
                        least = team[3]
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
                    if team[0] in occupied:  # the team is already playing
                        continue
                    if team[3] == least:  # if no team as played less than this one
                        if not team[1]:
                            team[1] = team[4].copy()
                        for team2 in group:
                            if team2[0] in team[1]:
                                if team2[0] not in occupied:
                                    # a game shall be played between team2 and team 1
                                    courts[court_to_fill] = [
                                        team[0],
                                        team2[0],
                                        group_no,
                                    ]
                                    if team[0] not in team2[1]:
                                        team2[1] = team2[4].copy()
                                    occupied.append(team2[0])
                                    occupied.append(team[0])
                                    team[3] += 1
                                    team[2].append(team2[0])
                                    team[1].remove(team2[0])
                                    team2[3] += 1
                                    team2[2].append(team[0])
                                    team2[1].remove(team[0])
                                    escape = True
                                    break

        # add referees
        for court in courts:
            group = groups[court[2]]
            found = False
            min_refs = 9999  # minimum number of games refereed by a team in the group
            best_team = 9999  # team with the least referees
            i = 0
            for team in group:  # try to find a ref from the same group
                if team[0] not in occupied:
                    if team[5] <= min_refs:
                        min_refs = team[5]
                        best_team = i
                        found = True
                i += 1
            if found:
                occupied.append(group[best_team][0])
                court[2] = group[best_team][0]
            else:  # find one from a different group
                match_up_score += 0.1
                for j in range(100):
                    group = groups[random.randint(0, len(groups) - 1)]
                    i = 0
                    for team in group:  # try to find a ref from the same group
                        if team[0] not in occupied:
                            if team[5] <= min_refs:
                                min_refs = team[5]
                                best_team = i
                                found = True
                        i += 1
                    if found:
                        occupied.append(group[best_team][0])
                        court[2] = group[best_team][0]
                        break
        to_output = []
        for court in courts:
            to_output.append(court[0])
            to_output.append(court[1])
            to_output.append(court[2])
        output_matrix.append(to_output)
    return match_up_score, output_matrix, groups


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
            # I would do "min_games = min(min_games,team[3])", but couldn't get it to work
            if min_games > team[3]:
                min_games = team[3]
            if max_games < team[3]:
                max_games = team[3]
            if min_g > team[3]:
                min_g = team[3]
            if max_g < team[3]:
                max_g = team[3]
            if min_used > team[3] + team[5]:
                min_used = team[3] + team[5]
            if max_used < team[3] + team[5]:
                max_used = team[3] + team[5]
        match_up_score += (max_g - min_g) * 2 + (max_used - min_used)
    match_up_score += (max_games - min_games) * 5
    # print(match_up_score)
    return match_up_score


if __name__ == "__main__":
    best_output_matrix, average_match_up_score, best_match_up_score = run_sims(original_groups)
    print_table(best_output_matrix)
    print(
        best_match_up_score,
        "best score compared to average of :",
        average_match_up_score,
    )
