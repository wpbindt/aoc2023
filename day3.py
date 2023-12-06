from dataclasses import dataclass, field
from itertools import groupby
from parsing import *


@dataclass
class Symbol:
    neighbors: set[tuple[int, int]] = field(default_factory=set)


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
    symbols = []
    for row_number, line in enumerate(parsed):
        for column_number, c in enumerate(line):
            if isinstance(c, Nothing):
                continue
            c.neighbors = get_neighbors(row_number, column_number)
            if isinstance(c, Symbol):
                symbols.append(c)

    numbers = []
    for line in parsed:
        for k, group in groupby(line, type):
            if k != Digit:
                continue
            numbers.append(sum(group, start=Digit('')))


    return parsed, numbers



assert symbol('boink').result == CouldNotParse()
for s in symbols:
    assert symbol(s).result == Symbol()
assert nothing('boink').result == CouldNotParse()
assert nothing('.').result == Nothing()
assert parts_line('..*&').result == [Nothing(), Nothing(), Symbol(), Symbol()]
assert parts_line('.3.*&').result == [Nothing(), Digit('3'), Nothing(), Symbol(), Symbol()], parts_line('.3.*&').result 
assert parts_document('.3.*&\n..4*.').result == [[Nothing(), Digit('3'), Nothing(), Symbol(), Symbol()], [Nothing(), Nothing(), Digit('4'), Symbol(), Nothing()]]

print(parse_document('.3.*&\n..4*.'))
