from ast import literal_eval


with open('day4_input', 'r') as f:
    lines = list(f)


scores = [
    len(parsed_line[0] & parsed_line[1])
    for parsed_line in map(literal_eval, lines)
]

print(sum(2 ** (score - 1) for score in scores if score != 0))

