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
    for coord in symbols_coordinates:
        relevant_numbers = []
        for number in numbers:
            if coord in number.neighbors:
                relevant_numbers.append(number)
            if len(relevant_numbers) > 2:
                break
        if len(relevant_numbers) == 2:
            result.append(int(relevant_numbers[0].digit) * int(relevant_numbers[1].digit))

    return result



assert symbol('boink').result == CouldNotParse()
for s in symbols:
    assert symbol(s).result == Symbol()
assert nothing('boink').result == CouldNotParse()
assert nothing('.').result == Nothing()
assert parts_line('..*&').result == [Nothing(), Nothing(), Symbol(), Symbol()]
assert parts_line('.3.*&').result == [Nothing(), Digit('3'), Nothing(), Symbol(), Symbol()], parts_line('.3.*&').result 
assert parts_document('.3.*&\n..4*.').result == [[Nothing(), Digit('3'), Nothing(), Symbol(), Symbol()], [Nothing(), Nothing(), Digit('4'), Symbol(), Nothing()]]

input_ = '\n'.join([
    '467..114..',
    '...*......',
    '..35..633.',
    '......#...',
    '617*......',
    '.....+.58.',
    '..592.....',
    '......755.',
    '...$.*....',
    '.664.598..',
])

assert sum(parse_document(input_)) == 467835

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
result = parse_document(lines)
print(sum(result))

