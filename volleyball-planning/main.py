from collections import defaultdict
import csv
import pulp
from pathlib import Path
from datetime import timedelta, datetime

ALPHABET = "abcdefghijklmnop"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
SLACK = 1000


def load_data():
    teams_to_league = {
        "BSJ1": "juniors",
        "BSJ2": "juniors",
        "BSL1": "womens1",
        "BSM1": "mens1",
        "BSM2": "mens2",
        "BSX1": "mixed1",
        "FBJ1": "juniors",
        "FBL1": "womens1",
        "FBM1": "mens1",
        "FBM2": "mens2",
        "FBX1": "mixed1",
        "MHL1": "womens1",
        "MHM1": "mens1",
        "MHM2": "mens2",
        "MHX1": "mixed1",
        "MHX2": "mixed1",
        "MVJ1": "juniors",
        "MVX1": "mixed2",
        "NBJ1": "juniors",
        "NBL1": "womens1",
        "NBM1": "mens2",
        "NBM2": "mens2",
        "NBX1": "mixed2",
        "OUL1": "womens1",
        "OUM1": "mens2",
        "OXL1": "womens1",
        "OXL2": "womens1",
        "OXM1": "mens1",
        "OXM2": "mens1",
        "OXM3": "mens1",
        "OXX1": "mixed1",
        "RAJ1": "juniors",
        "RAJ2": "juniors",
        "RAL1": "womens1",
        "RAM1": "mens1",
        "RAM2": "mens2",
        "RAM3": "mens2",
        "RAX1": "mixed1",
        "RAX2": "mixed2",
        "SBJ1": "juniors",
        "SBL1": "womens1",
        "SPL1": "womens1",
        "SPM1": "mens1",
        "SPM2": "mens1",
        "SPX1": "mixed1",
        "SPX2": "mixed2",
        "SPX3": "mixed2",
        "WEM1": "mens2",
        "WEX1": "mixed2",
    }
    teams_to_league = {
        team: league for (team, league) in teams_to_league.items() if league.startswith("mens") or league.startswith("womens")
    }
    leagues_to_teams = defaultdict(list)
    for team, league in teams_to_league.items():
        leagues_to_teams[league].append(team)
    team_clubs = {team: team[:2] for team in teams_to_league.keys()}

    club_venue_count = {
        "BS": 1,
        "FB": 1,
        "MH": 1,
        "MV": 1,
        "NB": 1,
        "OU": 1,
        "OX": 1,
        "RA": 1,
        "SB": 1,
        "SP": 2,
        "WE": 0,
    }

    # start_date = "13/10/2024"
    start_date = "05/10/2025"
    end_date = "26/04/2026"
    dates = generate_dates(
        start_date,
        end_date,
        exclude_dates={
            "21/12/2025",
            "28/12/2025",
            "29/03/2026",
            "19/04/2026",
        },
    )

    team_unavailabilities = [
        ("BSM1", "12/10/2025"),
        ("BSM1", "19/10/2025"),
        ("BSM1", "09/11/2025"),
        ("BSM1", "07/12/2025"),
        ("FBJ1", "07/12/2025"),
        ("BSL1", "12/10/2025"),
        ("BSL1", "07/12/2025"),
        ("MHL1", "15/03/2026"),
        # To make the problem feasible, we enable these dates
        # ("OUL1", "30/11/2025"),
        # ("OUL1", "07/12/2025"),
        # ("OUL1", "14/12/2025"),
        ("OUL1", "04/01/2026"),
        ("OUL1", "08/03/2026"),
        ("OUL1", "15/03/2026"),
        ("OUL1", "22/03/2026"),
        ("OUL1", "29/03/2026"),
        ("OUL1", "12/04/2026"),
        ("FBL1", "05/10/2025"),
        ("FBL1", "14/12/2025"),
        ("SBL1", "09/11/2025"),
        ("SBL1", "23/11/2025"),
        ("SBL1", "07/12/2025"),
        ("SBL1", "14/12/2025"),
        ("SBL1", "11/01/2026"),
        ("SBL1", "01/02/2026"),
        ("SBL1", "15/02/2026"),
        ("SBL1", "12/04/2026"),
        ("SBL1", "19/04/2026"),
        ("SBL1", "26/04/2026"),
        ("BSM2", "23/11/2025"),
        ("BSM2", "12/04/2026"),
        ("OUM1", "05/10/2025"),
        ("OUM1", "30/11/2025"),
        ("OUM1", "07/12/2025"),
        ("OUM1", "14/12/2025"),
        ("OUM1", "04/01/2026"),
        ("OUM1", "08/03/2026"),
        ("OUM1", "15/03/2026"),
        ("OUM1", "22/03/2026"),
        ("OUM1", "29/03/2026"),
        ("OUM1", "12/04/2026"),
        ("WEM1", "19/10/2025"),
        ("WEM1", "09/11/2025"),
        ("WEM1", "16/11/2025"),
        ("WEM1", "07/12/2025"),
        ("WEM1", "01/02/2026"),
        ("WEM1", "08/02/2026"),
        ("WEX1", "19/10/2025"),
        ("WEX1", "09/11/2025"),
        ("WEX1", "16/11/2025"),
        ("WEX1", "07/12/2025"),
        ("WEX1", "01/02/2026"),
        ("WEX1", "08/02/2026"),
        ("MHX1", "15/03/2026"),
        ("MHX2", "15/03/2026"),
    ]
    team_unavailabilities = [(team, date_) for team, date_ in team_unavailabilities if team in team_clubs and date_ in dates]

    venue_unavailabilities = [
        ("BS", "07/12/2025"),
        ("FB", "14/12/2025"),
        ("MV", "11/01/2026"),
        ("MV", "18/01/2026"),
        ("MV", "25/01/2026"),
        ("MV", "01/02/2026"),
        ("MV", "08/02/2026"),
        ("MV", "15/02/2026"),
        ("MV", "22/02/2026"),
        ("MV", "01/03/2026"),
        ("MV", "08/03/2026"),
        ("MV", "22/03/2026"),
        ("MV", "12/04/2026"),
        ("MV", "19/04/2026"),
        ("MV", "26/04/2026"),
    ]
    venue_unavailabilities = [(club, date_) for club, date_ in venue_unavailabilities if date_ in dates]

    return {
        "leagues_to_teams": leagues_to_teams,
        "teams_to_league": teams_to_league,
        "teams_to_club": team_clubs,
        "team_unavailabilities": team_unavailabilities,
        "venue_unavailabilities": venue_unavailabilities,
        "dates": dates,
        "club_venue_count": club_venue_count,
    }


def generate_dates(start_date, end_date, exclude_dates):
    start_date = datetime.strptime(start_date, "%d/%m/%Y").date()
    end_date = datetime.strptime(end_date, "%d/%m/%Y").date()
    exclude_dates = {datetime.strptime(d, "%d/%m/%Y").date() for d in exclude_dates}
    now = start_date
    dates = [start_date]

    while True:
        now = now + timedelta(days=14)
        if now <= end_date:
            if now not in exclude_dates:
                dates.append(now)
        else:
            break
    return [d.strftime("%d/%m/%Y") for d in dates]


def get_matches_for_league(teams: list[str]):
    megadict = {
        9: [
            [{8, 0, 4}, {1, 5, 7}, {2, 3, 6}],
            [{8, 1, 6}, {0, 2, 5}, {3, 4, 7}],
            [{0, 1, 3}, {8, 2, 7}, {4, 5, 6}],
            [{0, 6, 7}, {1, 2, 4}, {8, 3, 5}],
            [{0, 8, 4}, {1, 5, 6}, {2, 3, 7}],
            [{0, 1, 2}, {3, 4, 5}, {8, 6, 7}],
            [{0, 5, 7}, {8, 1, 3}, {2, 4, 6}],
            [{0, 3, 6}, {1, 4, 7}, {8, 2, 5}],
        ],
        10: [
            [{0, 3, 5}, {1, 4, 9}, {8, 2, 6}],
            [{8, 0, 4}, {1, 5, 6}, {9, 2, 7}],
            [{0, 9, 6}, {8, 2, 3}, {4, 5, 7}],
            [{2, 4, 5}, {3, 6, 7}, {8, 9, 1}],
            [{0, 4, 7}, {9, 3, 5}],
            [{0, 2, 7}, {1, 3, 4}, {8, 5, 6}],
            [{1, 5, 7}, {2, 4, 6}, {0, 9, 3}],
            [{9, 4, 6}, {8, 3, 7}, {0, 1, 2}],
            [{8, 4, 5}, {1, 6, 7}],
            [{0, 1, 8}, {9, 2, 5}, {3, 4, 6}],
            [{8, 9, 7}, {1, 2, 3}, {0, 5, 6}],
        ],
    }
    schedule = megadict[len(teams)]

    schedule_with_names = [[{teams[idx] for idx in match} for match in day] for day in schedule]
    new_schedule = [(match_day_num, teams) for match_day_num, match_day in enumerate(schedule_with_names) for teams in match_day]
    return new_schedule


def get_match_date_preferences(dates, matches: list[tuple[int, set[str]]]) -> list[list[float]]:
    n_dates = len(dates)
    match_days = set(match_day for match_day, _ in matches)
    n_match_days = len(match_days)
    all_preferences = []
    for match_day, _ in matches:
        fraction_through = match_day / (n_match_days - 1)  # convert to a 0-1 range
        ideal_date_index = fraction_through * (n_dates - 1)
        match_day_preferences = [0.5 ** abs(date_index - ideal_date_index) for date_index in range(n_dates)]
        all_preferences.append(match_day_preferences)
    return all_preferences


def solve_problem(data: dict):
    problem = pulp.LpProblem("volleyball-planning", pulp.LpMinimize)

    leagues_to_teams = defaultdict(list)
    for team, league in data["teams_to_league"].items():
        leagues_to_teams[league].append(team)
    data["leagues"] = sorted(leagues_to_teams.keys())
    club_to_teams = defaultdict(list)
    for team, club in data["teams_to_club"].items():
        club_to_teams[club].append(team)
    clubs = sorted(club_to_teams.keys())
    leagues_to_matches = {league: get_matches_for_league(teams_in_league) for league, teams_in_league in leagues_to_teams.items()}
    teams_to_matches = {
        team: {match for match, (_, teams_for_match) in enumerate(leagues_to_matches[league]) if team in teams_for_match}
        for team, league in data["teams_to_league"].items()
    }
    league_match_to_preferred_dates = {
        league: get_match_date_preferences(data["dates"], matches) for league, matches in leagues_to_matches.items()
    }

    check_availabilities(data, leagues_to_matches)

    # This is assigning each leagues' match days to particular dates
    matches_vs_dates = {
        league: {
            match: {date: pulp.LpVariable(name=f"matches_vs_dates{league}_{match}_{date}", cat="Binary") for date in data["dates"]}
            for match in range(len(leagues_to_matches[league]))
        }
        for league in data["leagues"]
    }
    venue_bookings = {
        club: {
            league: {
                date: {
                    match: pulp.LpVariable(name=f"venue_bookings_{club}_{date}_{match}_{league}", cat="Binary")
                    for match in range(len(leagues_to_matches[league]))
                }
                for date in data["dates"]
            }
            for league in data["leagues"]
        }
        for club in clubs
    }
    slack_unfair_club_home_matches = {club: pulp.LpVariable(name=f"slack_unfair_club_home_matches_{club}", lowBound=0) for club in clubs}
    slack_unfair_team_home_matches = {
        team: pulp.LpVariable(name=f"slack_unfair_team_home_matches_{team}", lowBound=0) for team in data["teams_to_league"].keys()
    }

    # Clubs must not be overbooked
    for club in clubs:
        for date in data["dates"]:
            problem += (
                pulp.lpSum(
                    venue_bookings[club][league][date][match]
                    for league in data["leagues"]
                    for match in range(len(leagues_to_matches[league]))
                )
                <= data["club_venue_count"][club]
            )

    # Match day logic
    for league in data["leagues"]:
        # Each match must happen exactly once
        for match in range(len(leagues_to_matches[league])):
            problem += pulp.lpSum(matches_vs_dates[league][match][date] for date in data["dates"]) == 1

        # We must book a venue for each match, matching the teams in the match
        for match, (_, relevant_teams) in enumerate(leagues_to_matches[league]):
            relevant_clubs = {data["teams_to_club"][team] for team in relevant_teams}

            for date in data["dates"]:
                problem += matches_vs_dates[league][match][date] <= pulp.lpSum(
                    venue_bookings[club][league][date][match] for club in relevant_clubs
                )

        # We are only allowed to play one match per team per date
        for team in leagues_to_teams[league]:
            relevant_matches = teams_to_matches[team]
            for date in data["dates"]:
                problem += pulp.lpSum(matches_vs_dates[league][match][date] for match in relevant_matches) <= 1

    club_match_count = defaultdict(int)
    team_match_count = defaultdict(int)
    for league, matches in leagues_to_matches.items():
        for _, match in matches:
            for team in match:
                club = data["teams_to_club"][team]
                club_match_count[club] += 1
                team_match_count[team] += 1

    for club in clubs:
        # Need the +1, otherwise we end up with infeasibilities for clubs with e.g. 8 matches
        fair_number_of_bookings = club_match_count[club] / 3 + 1
        problem += (
            pulp.lpSum(
                venue_bookings[club][league][date][match]
                for league, matches in leagues_to_matches.items()
                for match in range(len(matches))
                for date in data["dates"]
            )
            <= fair_number_of_bookings + slack_unfair_club_home_matches[club]
        )
    for team, club in data["teams_to_club"].items():
        # Need the +1, otherwise we end up with infeasibilities for clubs with e.g. 8 matches
        league = data["teams_to_league"][team]
        fair_number_of_bookings = team_match_count[team] / 3 + 1
        problem += (
            pulp.lpSum(venue_bookings[club][league][date][match] for match in teams_to_matches[team] for date in data["dates"])
            <= fair_number_of_bookings + slack_unfair_team_home_matches[team]
        )

    for team, date in data["team_unavailabilities"]:
        relevant_matches = teams_to_matches[team]
        league = data["teams_to_league"][team]
        for match in relevant_matches:
            problem += matches_vs_dates[league][match][date] == 0

    for club, date in data["venue_unavailabilities"]:
        if club not in venue_bookings:
            # Club MV only has juniors & mixed, so skip here.
            continue
        for league, matches in leagues_to_matches.items():
            for match in range(len(matches)):
                problem += venue_bookings[club][league][date][match] == 0

    # Objective function
    problem += (
        pulp.lpSum(
            -preference * matches_vs_dates[league][match][date]  # Preference is 0-1, with 1 the most preferred, therefore flip the sign
            for league, match_to_preferred_dates in league_match_to_preferred_dates.items()
            for match, preferred_dates in enumerate(match_to_preferred_dates)
            for date, preference in zip(data["dates"], preferred_dates, strict=True)
        )
        + 1000 * pulp.lpSum(slack_unfair_club_home_matches[club] for club in clubs)
        + 0.1 * pulp.lpSum(slack_unfair_team_home_matches[team] for team in data["teams_to_club"].keys())
    )

    problem.solve()
    if (solve_status := pulp.LpStatus[problem.status]) != "Optimal":
        raise ValueError(f"solve status {solve_status}")

    sovled_match_dates = [
        (league, match, date)
        for league, inner_dict1 in matches_vs_dates.items()
        for match, inner_dict2 in inner_dict1.items()
        for date, lp_var in inner_dict2.items()
        if lp_var.varValue > 0.5
    ]
    print("sovled_match_dates", sovled_match_dates)
    # alt_venue_bookings = dict_var_to_dict_val(venue_bookings, filter_zero=True)
    # print(alt_venue_bookings)
    clubs_used_for_games = {}
    for league in data["leagues"]:
        for date in data["dates"]:
            for match in range(len(leagues_to_matches[league])):
                for club in clubs:
                    if venue_bookings[club][league][date][match].varValue > 0.5:
                        # match found
                        key = (league, date, match)
                        # assert key not in clubs_used_for_games
                        clubs_used_for_games[key] = club

    fixtures = sorted(
        [
            league,
            date,
            match,
            clubs_used_for_games[(league, date, match)],
            leagues_to_matches[league][match][1],
        ]
        for league, inner_dict1 in matches_vs_dates.items()
        for match, inner_dict2 in inner_dict1.items()
        for date, lp_var in inner_dict2.items()
        if lp_var.varValue > 0.5
    )
    print("clubs_used_for_games", clubs_used_for_games)
    print("fixtures", fixtures)
    return fixtures


def dict_var_to_dict_val(input_val: dict | pulp.LpVariable, filter_zero=False):
    if isinstance(input_val, pulp.LpVariable):
        if filter_zero and input_val.varValue == 0:
            return None
        else:
            return input_val.varValue
    elif isinstance(input_val, dict):
        result = {key: new_val for key, val in input_val.items() if (new_val := dict_var_to_dict_val(val, filter_zero)) is not None}
        if filter_zero and len(result) == 0:
            return None
        else:
            return result
    else:
        raise ValueError


def check_availabilities(data: dict, leagues_to_matches: dict):
    # Note, this doesn't guarantee availability is sufficient, but it should catch the worst cases.
    total_unavailaiblities = defaultdict(int)
    for team, _ in data["team_unavailabilities"]:
        total_unavailaiblities[team] += 1
    for league, matches in leagues_to_matches.items():
        num_match_days = max(match_day_num for (match_day_num, teams) in matches) + 1
        max_unavailabilites = len(data["dates"]) - num_match_days
        if max_unavailabilites < 0:
            raise ValueError(f"Too few dates ({len(data['dates'])}) for the number of match dates ({num_match_days})")
        bad_teams = [
            (team, total_unavailaiblities[team])
            for team in data["leagues_to_teams"][league]
            if total_unavailaiblities[team] > max_unavailabilites
        ]
        if bad_teams:
            raise ValueError(
                f"The following teams have too many relevant unavailable dates, given that we have {len(data['dates'])} dates and {num_match_days} matches, we can only have {max_unavailabilites} days off: {bad_teams}"
            )


def write_outputs(data, fixtures: list[tuple]):
    # Sort so that home teams go first
    for fixture in fixtures:
        fixture[4] = sorted(fixture[4], key=lambda team_name: team_name[:2] != fixture[3])

    long_single_format = [
        (
            match_fixture[0],
            match_fixture[1],
            match_fixture[2],
            match_fixture[3],
            team,
            int(team[:2] == match_fixture[3]),
        )
        for match_fixture in fixtures
        for team in match_fixture[-1]
    ]
    long_single_format = sorted(long_single_format, key=lambda row: (row[0], datetime.strptime(row[1], "%d/%m/%Y"), row[2]))
    with open(OUTPUT_DIR / "long_fixtures.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["league", "date", "match_number", "Host club", "team", "is_home_match"])
        writer.writerows(long_single_format)

    date_to_date_number = {date: i + 1 for i, date in enumerate(data["dates"])}
    team_to_team_letter = {team: ALPHABET[team_idx] for teams in data["leagues_to_teams"].values() for team_idx, team in enumerate(teams)}

    # Restructure fixtures so that we can produce lomo output
    structured_games = {league: {date: [] for date in data["dates"]} for league in data["leagues_to_teams"].keys()}
    for league, date, match_number, host_club, teams in fixtures:
        teams = sorted(teams, key=lambda team_name: team_name[:2] != host_club)
        games = [
            # print the away (or away-ish) teams first
            sort_and_format_pair(teams[1], teams[2], host_club, team_to_team_letter),
            sort_and_format_pair(teams[0], teams[2], host_club, team_to_team_letter),
            sort_and_format_pair(teams[0], teams[1], host_club, team_to_team_letter),
        ]
        structured_games[league][date].extend(games)

    # Send friendlies to the last on their triangular
    possible_friendlies = {
        9: [],
        10: [("e", "f"), ("e", "g"), ("f", "g")],
    }
    found_friendlies = {}
    for league, league_dict in structured_games.items():
        num_teams = len(data["leagues_to_teams"][league])
        remaining_friendlies = set(possible_friendlies[num_teams])
        found_friendlies[league] = []
        for date in reversed(data["dates"]):
            # Try to schedule friendlies as late as possible in the season
            date_list = league_dict[date]
            for idx in range(len(date_list)):
                teams_to_play = date_list[idx]
                if teams_to_play in remaining_friendlies:
                    # found a friendly!
                    for offset in [2, 1]:
                        try:
                            swap_candidate = date_list[idx + offset]
                        except IndexError:
                            continue
                        if teams_to_play[0] in swap_candidate or teams_to_play[1] in swap_candidate:
                            # swap_candidate is part of the same triangular, so we can move the friendly to the back of the triangular
                            date_list[idx], date_list[idx + offset] = date_list[idx + offset], date_list[idx]
                            break

                    # cleanup
                    remaining_friendlies.remove(teams_to_play)
                    found_friendlies[league].append((date, teams_to_play))
        assert not remaining_friendlies

    # add in "free" games
    for league, league_dict in structured_games.items():
        all_teams = {team_to_team_letter[team] for team in data["leagues_to_teams"][league]}
        for date, date_list in league_dict.items():
            pass
            all_present_teams = set(team for match in date_list for team in match)
            missing_teams = sorted(all_teams.difference(all_present_teams))
            date_list.extend((team, "free") for team in missing_teams)

    # actually write out the triangular:
    for league, league_dict in structured_games.items():
        with open(OUTPUT_DIR / f"triangulars_{league}.csv", "w") as triangular_file:
            for date in data["dates"]:
                date_num = date_to_date_number[date]
                for team0, team1 in league_dict[date]:
                    triangular_file.write(f"{date_num},{team0},{team1}\n")

    # write out other outputs
    date_output = sorted((date_num, date) for date, date_num in date_to_date_number.items())
    with open(OUTPUT_DIR / "date_numbers.csv", "w") as date_file:
        for date_num, date in date_output:
            date_file.write(f"{date_num},{date}\n")
    for league, teams in data["leagues_to_teams"].items():
        team_letter_output = sorted((team_to_team_letter[team], team) for team in teams)
        with open(OUTPUT_DIR / f"teams_{league}.csv", "w") as date_file:
            for team_letter, team in team_letter_output:
                date_file.write(f"{team_letter},{team}\n")
    with open(OUTPUT_DIR / "friendlies.csv", "w") as friendlies_file:
        for league, league_list in found_friendlies.items():
            for date, (team0, team1) in league_list:
                team0 = data["leagues_to_teams"][league][ALPHABET.find(team0)]
                team1 = data["leagues_to_teams"][league][ALPHABET.find(team1)]
                friendlies_file.write(f"{league}, {date}, {team0}, {team1}\n")


def sort_and_format_pair(team0, team1, host_club, team_to_team_letter):
    pair = sorted(
        [team0, team1],
        key=lambda team_name: (team_name[:2] != host_club, team_name),
    )

    return tuple(team_to_team_letter[team] for team in pair)


def main():
    data = load_data()
    # print(data)
    fixtures = solve_problem(data)
    write_outputs(data, fixtures)


if __name__ == "__main__":
    main()

# Caveats:
# Can't split up match days currently. This is probably doable, but is more work ofc.
#   Hm, need to add a constraint to ensure I can't double-book a team
# We allocate games through the season, and ensure that each club gets a fair number of home games, but we don't ensure that the home games are distributed through the season
# It is not possible to get a perfectly fair number of home games: if you have 8 matches, you can't have exactly 1/3rd at home. Therefore, there is a bit of fuzziness.
