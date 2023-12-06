from dataclasses import dataclass
from parsing import *


@dataclass(frozen=True)
class Symbol:
    pass


@dataclass(frozen=True)
class Nothing:
    pass


symbols = {'$', '%', '@', '-', '=', '/', '#', '*', '+', '&'}
symbol: Parser[Symbol] = apply(
    lambda t: Symbol(), 
    or_(*(
        word(s)
        for s in symbols
    ))
)
nothing = apply(lambda t: Nothing(), word('.'))
parts_line = many(or_(symbol, nothing, digit))
parts_document = separated_by(parts_line, '\n')

assert symbol('boink').result == CouldNotParse()
for s in symbols:
    assert symbol(s).result == Symbol()
assert nothing('boink').result == CouldNotParse()
assert nothing('.').result == Nothing()
assert parts_line('..*&').result == [Nothing(), Nothing(), Symbol(), Symbol()]
assert parts_line('.3.*&').result == [Nothing(), '3', Nothing(), Symbol(), Symbol()]
assert parts_document('.3.*&\n..4*.').result == [[Nothing(), '3', Nothing(), Symbol(), Symbol()], [Nothing(), Nothing(), '4', Symbol(), Nothing()]]

