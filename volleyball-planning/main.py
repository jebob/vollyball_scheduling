from collections import defaultdict
import math
import pulp

TEAM_SLOTS = "abcdefghijklmnop"


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
    teams_to_league = {team: league for (team, league) in teams_to_league.items() if league == "M1"}
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


def get_match_days_for_league_size(size: int):
    megadict = {
        9: [
            [
                (1, "i", "e"),
                (1, "a", "i"),
                (1, "a", "e"),
                (1, "h", "f"),
                (1, "b", "h"),
                (1, "b", "f"),
                (1, "d", "g"),
                (1, "c", "d"),
                (1, "c", "g"),
            ],
            [
                (2, "g", "b"),
                (2, "i", "g"),
                (2, "i", "b"),
                (2, "a", "c"),
                (2, "f", "a"),
                (2, "f", "c"),
                (2, "e", "h"),
                (2, "d", "e"),
                (2, "d", "h"),
            ],
            [
                (3, "b", "d"),
                (3, "a", "b"),
                (3, "a", "d"),
                (3, "c", "h"),
                (3, "i", "c"),
                (3, "i", "h"),
                (3, "f", "g"),
                (3, "e", "f"),
                (3, "e", "g"),
            ],
            [
                (4, "a", "g"),
                (4, "h", "a"),
                (4, "h", "g"),
                (4, "c", "e"),
                (4, "b", "c"),
                (4, "b", "e"),
                (4, "f", "i"),
                (4, "d", "f"),
                (4, "d", "i"),
            ],
            [
                (5, "a", "i"),
                (5, "e", "a"),
                (5, "e", "i"),
                (5, "g", "b"),
                (5, "f", "g"),
                (5, "f", "b"),
                (5, "h", "d"),
                (5, "c", "h"),
                (5, "c", "d"),
            ],
            [
                (6, "b", "c"),
                (6, "a", "b"),
                (6, "a", "c"),
                (6, "e", "f"),
                (6, "d", "e"),
                (6, "d", "f"),
                (6, "h", "i"),
                (6, "g", "h"),
                (6, "g", "i"),
            ],
            [
                (7, "f", "a"),
                (7, "h", "f"),
                (7, "h", "a"),
                (7, "b", "d"),
                (7, "i", "b"),
                (7, "i", "d"),
                (7, "g", "e"),
                (7, "c", "g"),
                (7, "c", "e"),
            ],
            [
                (8, "d", "a"),
                (8, "g", "d"),
                (8, "g", "a"),
                (8, "e", "h"),
                (8, "b", "e"),
                (8, "b", "h"),
                (8, "i", "c"),
                (8, "f", "i"),
                (8, "f", "c"),
            ],
        ]
    }
    return megadict[size]


def get_match_slots_for_league_size(size: int):
    return int(math.ceil(size / 3))


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
    # leagues_to_match_days = {
    #     league: get_match_days_for_league_size(len(teams_in_league))
    #     for league, teams_in_league in leagues_to_teams.items()
    # }
    leagues_to_match_slots = {
        league: get_match_slots_for_league_size(len(teams_in_league))
        for league, teams_in_league in leagues_to_teams.items()
    }
    # match_days_vs_dates = {
    #     league: {
    #         match_day: {
    #             date: pulp.LpVariable(name=f"match_days_vs_dates_{league}_{match_day}_{date}", cat="Binary")
    #             for date in data["dates"]
    #         }
    #         for match_day in range(len(leagues_to_match_days[league]))
    #     }
    #     for league in data["leagues"]
    # }
    # teams_vs_team_slots = {
    #     league: {
    #         team: {
    #             team_slot: pulp.LpVariable(name=f"teams_vs_team_slots_{league}_{team}_{team_slot}", cat="Binary")
    #             for team_slot in TEAM_SLOTS[:len(leagues_to_teams[league])]
    #         }
    #         for team in leagues_to_teams[league]
    #     }
    #     for league in data["leagues"]
    # }
    match_slots_active = {
        league: {
            date: {
                match_slot: pulp.LpVariable(name=f"match_slots_active_{league}_{date}_{match_slot}", cat="Binary")
                for match_slot in range(leagues_to_match_slots[league])
            }
            for date in data["dates"]
        }
        for league in data["leagues"]
    }
    teams_vs_match_slots = {
        league: {
            team: {
                date: {
                    match_slot: pulp.LpVariable(
                        name=f"teams_vs_match_slots_{league}_{team}_{date}_{match_slot}", cat="Binary"
                    )
                    for match_slot in range(leagues_to_match_slots[league])
                }
                for date in data["dates"]
            }
            for team in leagues_to_teams[league]
        }
        for league in data["leagues"]
    }
    home_games_vs_match_slots = {
        league: {
            date: {
                match_slot: {
                    club: pulp.LpVariable(
                        name=f"home_games_vs_match_slots_{league}_{date}_{match_slot}_{club}", cat="Binary"
                    )
                    for club in clubs
                }
                for match_slot in range(leagues_to_match_slots[league])
            }
            for date in data["dates"]
        }
        for league in data["leagues"]
    }
    # match slot logic
    for league in data["leagues"]:
        for date in data["dates"]:
            # Active match slots have three teams, inactive slots have no teams
            for match_slot in range(leagues_to_match_slots[league]):
                problem += (
                    pulp.lpSum(
                        teams_vs_match_slots[league][team][date][match_slot] for team in leagues_to_teams[league]
                    )
                    == match_slots_active[league][date][match_slot] * 3
                )
            # Teams can only participate in <=1 match slot/day
            for team in leagues_to_teams[league]:
                problem += (
                    pulp.lpSum(
                        teams_vs_match_slots[league][team][date][match_slot]
                        for match_slot in range(leagues_to_match_slots[league])
                    )
                    <= 1
                )

            for match_slot in range(leagues_to_match_slots[league]):
                # active match slots need a venue
                problem += (
                    pulp.lpSum(home_games_vs_match_slots[league][date][match_slot][club] for club in clubs)
                    == match_slots_active[league][date][match_slot]
                )

                # the venue must match at least one of the teams
                for club in clubs:
                    problem += home_games_vs_match_slots[league][date][match_slot][club] <= pulp.lpSum(
                        teams_vs_match_slots[league][team][date][match_slot] for team in club_to_teams[club]
                    )

        # temp: force some matches
        for team in leagues_to_teams[league]:
            problem += (
                pulp.lpSum(
                    teams_vs_match_slots[league][team][date][match_slot]
                    for date in data["dates"]
                    for match_slot in range(leagues_to_match_slots[league])
                )
                >= 1
            )
            problem += (
                pulp.lpSum(
                    teams_vs_match_slots[league][team][date][match_slot]
                    for date in data["dates"]
                    for match_slot in range(leagues_to_match_slots[league])
                )
                <= 2
            )
    # Clubs must not be overbooked
    for club in clubs:
        for date in data["dates"]:
            problem += (
                pulp.lpSum(
                    home_games_vs_match_slots[league][date][match_slot][club]
                    for league in data["leagues"]
                    for match_slot in range(leagues_to_match_slots[league])
                )
                <= data["club_venue_count"]
            )
    # todo: clubs must have no more than venues (mostly 1, sometimes 2) games per slot

    # # Match day logic
    # for league in data["leagues"]:
    #     # For each league, each team fills one team slot
    #     for team in leagues_to_teams[league]:
    #         problem += pulp.lpSum(teams_vs_team_slots[league][team][team_slot] for team_slot in TEAM_SLOTS[:len(leagues_to_teams[league])]) == 1
    #     # and each team slot has one team
    #     for team_slot in TEAM_SLOTS[:len(leagues_to_teams[league])]:
    #         problem += pulp.lpSum(teams_vs_team_slots[league][team][team_slot] for team in leagues_to_teams[league]) == 1

    # # Each match day must happen exactly once
    # for league in data["leagues"]:
    #     for match_day in range(len(leagues_to_match_days[league])):
    #         problem += pulp.lpSum(match_days_vs_dates[league][match_day][date] for date in data["dates"]) == 1

    # # For each league, no more than one match day must happen per date
    # for league in data["leagues"]:
    #     for date in data["dates"]:
    #         problem += (
    #             pulp.lpSum(
    #                 match_days_vs_dates[league][match_day][date]
    #                 for match_day in range(len(leagues_to_match_days[league]))
    #             )
    #             <= 1
    #         )
    # todo: make a variable for team vs date

    problem.solve()
    if (solve_status := pulp.LpStatus[problem.status]) != "Optimal":
        raise ValueError(f"solve status {solve_status}")

    # sovled_match_day_dates = [
    #     (league, match_day, date)
    #     for league, inner_dict1 in match_days_vs_dates.items()
    #     for match_day, inner_dict2 in inner_dict1.items()
    #     for date, lp_var in inner_dict2.items()
    #     if lp_var.varValue > 0.5
    # ]
    # print(sovled_match_day_dates)
    clubs_used_for_games = {}
    for league in data["leagues"]:
        for date in data["dates"]:
            for match_slot in range(leagues_to_match_slots[league]):
                for club in clubs:
                    if home_games_vs_match_slots[league][date][match_slot][club].varValue > 0.5:
                        # match found
                        key = (league, date, match_slot)
                        assert key not in clubs_used_for_games
                        clubs_used_for_games[key] = club
    fixtures = sorted(
        (league, date, clubs_used_for_games[(league, date, match_slot)], match_slot, team)
        for league, inner_dict1 in teams_vs_match_slots.items()
        for team, inner_dict2 in inner_dict1.items()
        for date, inner_dict3 in inner_dict2.items()
        for match_slot, lp_var in inner_dict3.items()
        if lp_var.varValue > 0.5
    )
    print(clubs_used_for_games)
    print(fixtures)


def main():
    data = load_data()
    print(data)
    solution = solve_problem(data)
    # construct then solve problem
    # write to outputs
    pass


if __name__ == "__main__":
    main()
