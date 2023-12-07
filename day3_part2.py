from dataclasses import dataclass, field
from itertools import groupby
from parsing import *


@dataclass
class Symbol:
    pass


@dataclass(frozen=True)
class Nothing:
    pass


@dataclass
class Digit:
    digit: str
    neighbors: set[tuple[int, int]] = field(default_factory=set)

    def __add__(self, other):
        return Digit(
            self.digit + other.digit,
            self.neighbors | other.neighbors
        )


N = Nothing
S = Symbol


symbols = {'$', '%', '@', '-', '=', '/', '#', '*', '+', '&'}
symbol: Parser[Symbol] = apply(
    lambda t: Symbol(), 
    or_(*(
        word(s)
        for s in symbols
    ))
)
nothing = apply(lambda t: Nothing(), word('.'))
our_digit = apply(lambda t: Digit(t), digit)
parts_line = many(or_(symbol, nothing, our_digit))

PartsDocument = list[list[Symbol | Nothing | str]]
parts_document: Parser[PartsDocument] = separated_by(parts_line, '\n')

def get_neighbors(row_number, column_number):
    return {
        (row_number + x, column_number + y)
        for x in {0, 1, -1}
        for y in {0, 1, -1}
    }

def parse_document(to_parse: str) -> PartsDocument:
    parsed = parts_document(to_parse).result
    symbols_coordinates = set()
    for row_number, line in enumerate(parsed):
        for column_number, c in enumerate(line):
            if isinstance(c, Nothing):
                continue
            if isinstance(c, Symbol):
                symbols_coordinates.add((row_number, column_number))
                continue
            c.neighbors = get_neighbors(row_number, column_number)

    numbers = []
    for line in parsed:
        for k, group in groupby(line, type):
            if k != Digit:
                continue
            numbers.append(sum(group, start=Digit('')))

    result = []
    for number in numbers:
        if len(number.neighbors & symbols_coordinates) > 0:
            result.append(number.digit)


    return list(map(int, result)), parsed



assert symbol('boink').result == CouldNotParse()
for s in symbols:
    assert symbol(s).result == Symbol()
assert nothing('boink').result == CouldNotParse()
assert nothing('.').result == Nothing()
assert parts_line('..*&').result == [Nothing(), Nothing(), Symbol(), Symbol()]
assert parts_line('.3.*&').result == [Nothing(), Digit('3'), Nothing(), Symbol(), Symbol()], parts_line('.3.*&').result 
assert parts_document('.3.*&\n..4*.').result == [[Nothing(), Digit('3'), Nothing(), Symbol(), Symbol()], [Nothing(), Nothing(), Digit('4'), Symbol(), Nothing()]]
res = parse_document('\n'.join([
    '.3.*..',
    '&..4*.',
    '&.5.*.',
]))
assert res[0] == [3, 4], res

res = parse_document('\n'.join([
    '.35*...',
    '...4*.9',
    '&.5.*..',
    '.......',
    '..#....',
    '...499.',
]))
assert res[0] == [35, 4, 499], res


res = parse_document('\n'.join([
    '...',
    '.3.',
    '...',
]))
assert res[0] == [], res
res = parse_document('\n'.join([
    '*..',
    '.3.',
    '...',
]))
assert res[0] == [3], res

res = parse_document('\n'.join([
    '...........822..174..*.....&...........711.746.......&............$....../.............656....#...........265=......634.*.............430...',
    '..827.137..*...*....39................*..............856..............767........522......$..773....619..............*...287....501.........',
    '..........726...511.............*.....320........476...............................*................%...899....72..731...........%....$.....',
    '...........822..174..*.....&...........711.746.......&............$....../.............656....#...........265=......634.*.............430...',
    '..827.137..*...*....39................*..............856..............767........522......$..773....619..............*...287....501.........',
    '..........726...511.............*.....320........476...............................*................%...899....72..731...........%....$.....',
    '.......502*80..960........................25........464.........831.846........25.........329..985...458.+.....&................377..659....',
]))
assert res[0] == [
    822, 174, 711, 656, 265, 634, 
    39, 856, 767, 522, 773, 619, 287, 501, 
    726, 511, 320, 731, 
    822, 174, 711, 656, 265, 634, 430, 
    39, 856, 767, 522, 773, 619, 287, 501,
    726, 511, 320, 899, 72, 731,
    502, 80, 458, 377, 659
], res

def print_parsed(parsed: PartsDocument) -> str:
    return '\n'.join(
        print_line(line)
        for line in parsed
    )

def print_line(line: list[S, N, Digit]):
    return ''.join(
        print_character(c)
        for c in line
    )

def print_character(c: N | S | Digit) -> str:
    if c == N():
        return '.'
    elif isinstance(c, S):
        return '*'
    else:
        return c.digit

with open('day3_input') as f:
    lines = ''.join([line for line in f])
    print(lines)
result, parsed = parse_document(lines)
assert 456 in result
print(sum(result))

