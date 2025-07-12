from collections import defaultdict
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

    start_date = "2022-10-16"
    end_date = "2023-04-30"
    dates = list(range(10, 20))
    return {
        "teams_to_league": teams_to_league,
        "team_clubs": team_clubs,
        "dates": dates,
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


def solve_problem(data: dict):
    problem = pulp.LpProblem("volleyball-planning", pulp.LpMinimize)

    leagues_to_teams = defaultdict(list)
    for team, league in data["teams_to_league"].items():
        leagues_to_teams[league].append(team)
    data["leagues"] = sorted(leagues_to_teams.keys())
    print(leagues_to_teams)

    leagues_to_match_days = {
        league: get_match_days_for_league_size(len(teams_in_league))
        for league, teams_in_league in leagues_to_teams.items()
    }
    match_days_vs_dates = {
        league: {
            match_day: {
                date: pulp.LpVariable(name=f"match_days_vs_dates_{league}_{match_day}_{date}", cat="Binary")
                for date in data["dates"]
            }
            for match_day in range(len(leagues_to_match_days[league]))
        }
        for league in data["leagues"]
    }
    teams_vs_team_slots = {
        league: {
            team: {
                team_slot: pulp.LpVariable(name=f"teams_vs_team_slots_{league}_{team}_{team_slot}", cat="Binary")
                for team_slot in TEAM_SLOTS[:len(leagues_to_teams[league])]
            }
            for team in leagues_to_teams[league]
        }
        for league in data["leagues"]
    }

    for league in data["leagues"]:
        # For each league, each team fills one team slot
        for team in leagues_to_teams[league]:
            problem += pulp.lpSum(teams_vs_team_slots[league][team][team_slot] for team_slot in TEAM_SLOTS[:len(leagues_to_teams[league])]) == 1
        # and each team slot has one team
        for team_slot in TEAM_SLOTS[:len(leagues_to_teams[league])]:
            problem += pulp.lpSum(teams_vs_team_slots[league][team][team_slot] for team in leagues_to_teams[league]) == 1

    # Each match day must happen exactly once
    for league in data["leagues"]:
        for match_day in range(len(leagues_to_match_days[league])):
            problem += pulp.lpSum(match_days_vs_dates[league][match_day][date] for date in data["dates"]) == 1

    # For each league, no more than one match day must happen per date
    for league in data["leagues"]:
        for date in data["dates"]:
            problem += (
                pulp.lpSum(
                    match_days_vs_dates[league][match_day][date]
                    for match_day in range(len(leagues_to_match_days[league]))
                )
                <= 1
            )
    # todo: make a variable for team vs date

    problem.solve()
    print(pulp.LpStatus[problem.status])

    sovled_match_day_dates = [
        (league, match_day, date)
        for league, inner_dict1 in match_days_vs_dates.items()
        for match_day, inner_dict2 in inner_dict1.items()
        for date, lp_var in inner_dict2.items()
        if lp_var.varValue > 0.5
    ]
    print(sovled_match_day_dates)


def main():
    data = load_data()
    print(data)
    solution = solve_problem(data)
    # construct then solve problem
    # write to outputs
    pass


if __name__ == "__main__":
    main()
