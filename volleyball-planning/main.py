from collections import defaultdict
import csv
import math
import pulp
from pathlib import Path

TEAM_SLOTS = "abcdefghijklmnop"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
SLACK = 1000


def load_data():
    teams_to_league = {
        "OXM1": "M1",
        "SPM1": "M1",
        "BSM1": "M1",
        "MHM1": "M1",
        "OXM2": "M1",
        "FBM1": "M1",
        "RAM1": "M1",
        "SPM2": "M1",
        "OXM3": "M1",
        "RAM2": "M2",
        "RAM3": "M2",
        "WEM1": "M2",
        "NBM1": "M2",
        "OUM1": "M2",
        "FBM2": "M2",
        "MHM2": "M2",
        "NBM2": "M2",
        "BSM2": "M2",
        "OXL1": "L1",
        "FBL1": "L1",
        "BSL1": "L1",
        "MHL1": "L1",
        "SPL1": "L1",
        "NBL1": "L1",
        "OXL2": "L1",
        "SBL1": "L1",
        "OUL1": "L1",
        "RAL1": "L1",
        "BSX1": "X1",
        "FBX1": "X1",
        "MHX1": "X1",
        "SPX1": "X1",
        "MHX2": "X1",
        "RAX1": "X1",
        "OXX1": "X1",
        "MVX1": "X2",
        "SPX2": "X2",
        "WEX1": "X2",
        "RAX2": "X2",
        "NBX1": "X2",
        "SPX3": "X2",
        "RAJ1": "J1",
        "MVJ1": "J1",
        "BSJ1": "J1",
        "NBJ1": "J1",
        "RAJ2": "J1",
        "FBJ1": "J1",
        "SBJ1": "J1",
        "BSJ2": "J1",
    }
    # For development purposes, just do M1
    teams_to_league = {team: league for (team, league) in teams_to_league.items() if league in ["M1"]}
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
    }

    start_date = "2022-10-16"
    end_date = "2023-04-30"
    dates = list(range(10, 20))
    return {
        "teams_to_league": teams_to_league,
        "teams_to_club": team_clubs,
        "dates": dates,
        "club_venue_count": club_venue_count,
    }


def get_matches_for_league(teams: list[str]):
    # TODO: test behaviour for a number of teams that isn't a multiple of 3.
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
    assert n_dates >= n_match_days
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
    league_match_to_preferred_dates = {
        league: get_match_date_preferences(data["dates"], matches) for league, matches in leagues_to_matches.items()
    }
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
    slack_unfair_matches = {club: pulp.LpVariable(name=f"slack_unfair_matches_{club}", lowBound=0) for club in clubs}

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
    # TODO: teams must never have two matches on the same date
    for league in data["leagues"]:
        # Each match must happen exactly once
        for match in range(len(leagues_to_matches[league])):
            problem += pulp.lpSum(matches_vs_dates[league][match][date] for date in data["dates"]) == 1

        # For each match day, we must book a venue for each match, matching the teams in the match
        for match, (_, relevant_teams) in enumerate(leagues_to_matches[league]):
            relevant_clubs = {data["teams_to_club"][team] for team in relevant_teams}

            for date in data["dates"]:
                problem += matches_vs_dates[league][match][date] <= pulp.lpSum(
                    venue_bookings[club][league][date][match] for club in relevant_clubs
                )

    club_match_slots = defaultdict(int)
    for league, matches in leagues_to_matches.items():
        for _, match in matches:
            for team in match:
                club = data["teams_to_club"][team]
                club_match_slots[club] += 1

    for club in clubs:
        # Need the +1, otherwise we end up with infeasibilities for clubs with e.g. 8 matches
        fair_number_of_bookings = club_match_slots[club] / 3 + 1
        problem += (
            pulp.lpSum(
                venue_bookings[club][league][date][match]
                for league, matches in leagues_to_matches.items()
                for match in range(len(matches))
                for date in data["dates"]
            )
            <= fair_number_of_bookings + slack_unfair_matches[club]
        )
        # TODO: ensure that each _team_ has a fair number of home matches

    # Objective function
    problem += pulp.lpSum(
        -preference * matches_vs_dates[league][match][date]  # Preference is 0-1, with 1 the most preferred, therefore flip the sign
        for league, match_to_preferred_dates in league_match_to_preferred_dates.items()
        for match, preferred_dates in enumerate(match_to_preferred_dates)
        for date, preference in zip(data["dates"], preferred_dates, strict=True)
    ) + pulp.lpSum(slack_unfair_matches[club] for club in clubs)

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
        (league, date, match, clubs_used_for_games[(league, date, match)], team)
        for league, inner_dict1 in matches_vs_dates.items()
        for match, inner_dict2 in inner_dict1.items()
        for date, lp_var in inner_dict2.items()
        for team in leagues_to_matches[league][match][1]
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


def write_outputs(fixtures: list[tuple]):
    with open(OUTPUT_DIR / "long_fixtures.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["league", "date", "match_number", "Host club", "team"])
        writer.writerows(fixtures)


def main():
    data = load_data()
    # print(data)
    fixtures = solve_problem(data)
    write_outputs(fixtures)


if __name__ == "__main__":
    main()

# Caveats:
# Can't split up match days currently. This is probably doable, but is more work ofc.
#   Hm, need to add a constraint to ensure I can't double-book a team
# We allocate games through the season, and ensure that each club gets a fair number of home games, but we don't ensure that the home games are distributed through the season
# It is not possible to get a perfectly fair number of home games: if you have 8 matches, you can't have exactly 1/3rd at home. Therefore, there is a bit of fuzziness.
