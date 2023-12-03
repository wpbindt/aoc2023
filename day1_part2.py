from dataclasses import dataclass
from enum import Enum, auto
from typing import Union, Iterator, Generic, Protocol, TypeVar


def parse_document(lines: list[str]) -> int:
    return sum(parse_line(line) for line in lines if line != '')


def parse_line(line: str) -> int:
    digits = [c for c in line if c in {str(i) for i in range(10)}]
    if len(digits) == 0:
        return 0
    return int(digits[0] + digits[-1])


class Digit(Enum):
    ONE = 'one'
    TWO = 'two'
    THREE = 'three'
    FOUR = 'four'
    FIVE = 'five'
    SIX = 'six'
    SEVEN = 'seven'
    EIGHT = 'eight'
    NINE = 'nine'



T = TypeVar('T')


@dataclass(frozen=True)
class CouldNotParse:
    pass


@dataclass(frozen=True)
class ParseResult(Generic[T]):
    result: T | CouldNotParse
    remainder: str


class Parser(Protocol[T]):
    def __call__(self, to_parse: str) -> ParseResult[T]:
        pass


def make_digit_parser(
    digit: str,
    result: Digit,
) -> Parser[Digit]:
    def parser(to_parse: str) -> ParseResult[Digit]:
        if to_parse.startswith(digit):
            return ParseResult(remainder=to_parse[1:], result=result)
        if to_parse.startswith(result.value):
            return ParseResult(remainder=to_parse[len(result.value):], result=result)
        return ParseResult(remainder=to_parse, result=CouldNotParse())
    return parser


def or_(*parsers: Parser[T]) -> Parser[T]:
    def parser(to_parse: str) -> ParseResult[T]:
        for parser in parsers:
            attempt = parser(to_parse)
            if attempt.result == CouldNotParse():
                continue
            return attempt
        return ParseResult(CouldNotParse(), to_parse)
    return parser


parse_digit: Parser[Digit] = or_(
    *(
        make_digit_parser(str(digit), result)
        for digit, result in enumerate(Digit, 1)
    )
)


def many(parser: Parser[T]) -> Parser[list[T]]:
    def parser_(to_parse: str) -> ParseResult[T]:
        results = []
        remainder = to_parse

        while True:
            result = parser(remainder)
            if result.result == CouldNotParse():
                break
            results.append(result.result)
            remainder = result.remainder
        return ParseResult(result=results, remainder=remainder)

    return parser_


assert parse_line('12') == 12
assert parse_line('1a3') == 13
assert parse_line('b3a8') == 38
assert parse_document(['b2c9', '1234']) == 29 + 14
assert parse_document(['b2c9', '', '1234']) == 29 + 14
assert parse_document(['b2c9', '\n', '1234']) == 29 + 14

parse_one = make_digit_parser('1', Digit.ONE)
parse_two = make_digit_parser('2', Digit.TWO)

assert parse_one('1').result == Digit.ONE
assert parse_one('one').result == Digit.ONE
assert parse_one('two').result == CouldNotParse()
assert parse_one('1a').remainder == 'a'
assert parse_one('onea').remainder == 'a'

assert parse_digit('two').result == Digit.TWO
assert parse_digit('one').result == Digit.ONE
assert parse_digit('six').result == Digit.SIX

assert many(parse_digit)('sixsix6').result == 3 * [Digit.SIX]
assert many(parse_digit)('').result == []

assert parse_document(['onetwo', '3afour', 'afive6', 'a7b8c']) == 12 + 34 + 56 + 78


with open('day1_input', 'r') as f:
    lines = [line for line in f]

print(parse_document(lines))

