import math

x = [
    [1, "a", "d"],
    [1, "f", "a"],
    [1, "f", "d"],
    [1, "e", "b"],
    [1, "j", "e"],
    [1, "j", "b"],
    [1, "g", "c"],
    [1, "i", "g"],
    [1, "i", "c"],
    [2, "i", "e"],
    [2, "a", "i"],
    [2, "a", "e"],
    [2, "b", "g"],
    [2, "f", "b"],
    [2, "f", "g"],
    [2, "h", "j"],
    [2, "c", "h"],
    [2, "c", "j"],
    [3, "g", "a"],
    [3, "j", "g"],
    [3, "j", "a"],
    [3, "d", "c"],
    [3, "i", "d"],
    [3, "i", "c"],
    [3, "f", "h"],
    [3, "e", "f"],
    [3, "e", "h"],
    [4, "c", "f"],
    [4, "e", "c"],
    [4, "e", "f"],
    [4, "g", "d"],
    [4, "h", "g"],
    [4, "h", "d"],
    [4, "j", "i"],
    [4, "b", "j"],
    [4, "b", "i"],
    [5, "h", "e"],
    [5, "a", "h"],
    [5, "a", "e"],
    [5, "j", "f"],
    [5, "d", "j"],
    [5, "d", "f"],
    [6, "a", "h"],
    [6, "c", "a"],
    [6, "c", "h"],
    [6, "d", "e"],
    [6, "b", "d"],
    [6, "b", "e"],
    [6, "f", "i"],
    [6, "g", "f"],
    [6, "g", "i"],
    [7, "f", "b"],
    [7, "h", "f"],
    [7, "h", "b"],
    [7, "c", "g"],
    [7, "e", "c"],
    [7, "e", "g"],
    [7, "d", "a"],
    [7, "j", "d"],
    [7, "j", "a"],
    [8, "e", "j"],
    [8, "g", "e"],
    [8, "g", "j"],
    [8, "i", "h"],
    [8, "d", "i"],
    [8, "d", "h"],
    [8, "b", "c"],
    [8, "a", "b"],
    [8, "a", "c"],
    [9, "f", "i"],
    [9, "e", "i"],
    [9, "e", "f"],
    [9, "h", "b"],
    [9, "g", "h"],
    [9, "g", "b"],
    [10, "b", "a"],
    [10, "i", "b"],
    [10, "i", "a"],
    [10, "j", "f"],
    [10, "c", "j"],
    [10, "c", "f"],
    [10, "d", "e"],
    [10, "d", "g"],
    [10, "e", "g"],
    [11, "i", "j"],
    [11, "h", "i"],
    [11, "h", "j"],
    [11, "c", "d"],
    [11, "b", "c"],
    [11, "b", "d"],
    [11, "a", "g"],
    [11, "f", "a"],
    [11, "f", "g"],
]

letters = "abcdefghij"

result = [[] for _ in range(20)]
for match_num, (day_num, team_a_str, team_b_str) in enumerate(x):
    team_a_int = letters.find(team_a_str)
    team_b_int = letters.find(team_b_str)
    day_group_num = math.floor(match_num / 3)

    for group in result[day_num]:
        if team_a_int in group:
            group.add(team_b_int)
            break
        elif team_b_int in group:
            group.add(team_a_int)
            break
    else:
        result[day_num].append({team_a_int, team_b_int})

result = [day for day in result if len(day)]

print(result)
