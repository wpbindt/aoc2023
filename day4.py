from parsing import *


def points(to_parse: str) -> int:
    pass

card_header = right(right(word('Card '), digit), word(': '))
integer = apply(int, apply(''.join, many_plus(digit)))
numbers = apply(set, separated_by_(integer, many_plus(word(' '))))
card = right(card_header, numbers)
winning_numbers = right(word(' | '), numbers)
game = and_(card, winning_numbers, lambda t, s: (t, s))


example_input = '\n'.join([
    'Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53',
    'Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19',
    'Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1',
    'Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83',
    'Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36',
    'Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11',
])

assert card_header('Card 1: ').result != CouldNotParse()
assert card_header('Card').result == CouldNotParse()
assert card_header('Card 1').result == CouldNotParse()

assert integer('13').result == 13

assert many(digit)('1234').result == ['1', '2', '3', '4']
assert separated_by_(digit, word(' '))('1 2 3').result == ['1', '2', '3']
assert separated_by_(digit, many_plus(word(' ')))('1 2 3').result == ['1', '2', '3']
assert separated_by_(apply(''.join, many(digit)), many_plus(word(' ')))('13 12 1').result == ['13', '12', '1']

assert numbers('1').result == {1}
assert numbers('13').result == {13}
assert numbers('13 12').result == {13, 12}
assert numbers('13 12  1').result == {13, 12, 1}

assert card('Card 1: 13 12  1').result == {13, 12, 1}

assert winning_numbers(' | 86  6 48 53').result == {86, 6, 48, 53}
assert and_(word('hi'), word(' | 86 6'), lambda t, s: s)('hi | 86 6').result == ' | 86 6'
assert and_(word('hi'), winning_numbers, lambda t, s: s)('hi | 86 6').result == {86, 6}
assert and_(numbers, winning_numbers, lambda t, s: (t, s))('41 48 | 86  6 48 53').result == ({41, 48}, {86, 6, 48, 53})
assert game('Card 1: 41 48 | 86  6 48 53').result == ({41, 48}, {86, 6, 48, 53})

assert points(example_input) == 13

