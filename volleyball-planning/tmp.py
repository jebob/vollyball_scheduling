import math

x = {
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

letters = "abcdefghi"

result = []
for day in x[9]:
    groups = []
    for match_num, (day_num, team_a_str, team_b_str) in enumerate(day):
        team_a_int = letters.find(team_a_str)
        team_b_int = letters.find(team_b_str)
        day_group_num = math.floor(match_num / 3)
        for group in groups:
            if team_a_int in group:
                group.add(team_b_int)
                break
            elif team_b_int in group:
                group.add(team_a_int)
                break
        else:
            groups.append({team_a_int, team_b_int})
    result.append(groups)

print(result)

