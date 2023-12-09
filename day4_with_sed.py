from ast import literal_eval
from typing import Iterator

with open('day4_input', 'r') as f:
    lines = list(f)

cards = list(map(literal_eval, lines))

# cards = [
#     ({41, 48, 83, 86, 17,},{83, 86,  6, 31, 17,  9, 48, 53}),
#     ({13, 32, 20, 16, 61,},{61, 30, 68, 82, 17, 32, 24, 19}),
#     ({ 1, 21, 53, 59, 44,},{69, 82, 63, 72, 16, 21, 14,  1}),
#     ({41, 92, 73, 84, 69,},{59, 84, 76, 51, 58,  5, 54, 83}),
#     ({87, 83, 26, 28, 32,},{88, 30, 70, 12, 93, 22, 82, 36}),
#     ({31, 18, 13, 56, 72,},{74, 77, 10, 23, 35, 67, 36, 11}),
# ]
def score_card(
    cards: list[tuple[set[int], set[int]]],
    index: int,
    top_level: bool = False
) -> list[int]:
    actual_numbers = cards[index][0]
    winning_numbers = cards[index][1]
    score = len(actual_numbers & winning_numbers)
    if score == 0:
        return []
    copies_won = list(range(index + 1, min(index + 1 + score, len(cards) - 1)))
    result = []
    result.extend(copies_won)
    for copy in copies_won:
        result.extend(score_card(cards, copy))
    return result

def notifying_iterator(upper_bound: int, notify_every: int) -> Iterator[int]:
    for ix in range(upper_bound):
        if ix % notify_every == 0:
            print(f'{ix} iterations out of {upper_bound} performed')
        yield ix

print(len(cards) + sum(map(len, [
    score_card(cards, index)
    for index in notifying_iterator(len(cards), 100)
])))


