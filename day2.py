from __future__ import annotations
from uuid import uuid4
from dataclasses import dataclass
from typing import Union, Iterator, Generic, Protocol, TypeVar
import string


T = TypeVar('T')


@dataclass(frozen=True)
class CouldNotParse:
    pass


@dataclass(frozen=True)
class ParseResult(Generic[T]):
    result: T | CouldNotParse
    remainder: str

    @classmethod
    def failure(cls, to_parse: str) -> ParseResult:
        return ParseResult(result=CouldNotParse(), remainder=to_parse)


class Parser(Protocol[T]):
    def __call__(self, to_parse: str) -> ParseResult[T]:
        pass


def digit(to_parse: str) -> ParseResult[str]:
    if not to_parse[0].isdigit():
        return ParseResult.failure(to_parse)
    return ParseResult(result=to_parse[0], remainder=to_parse[1:])


def or_(*parsers: Parser[T]) -> Parser[T]:
    def parser(to_parse: str) -> ParseResult[T]:
        for parser in parsers:
            attempt = parser(to_parse)
            if attempt.result == CouldNotParse():
                continue
            return attempt
        return ParseResult(CouldNotParse(), to_parse)
    return parser


def many(parser: Parser[T]) -> Parser[list[T]]:
    def parser_(to_parse: str) -> ParseResult[T]:
        result = parser(to_parse)
        if result.result == CouldNotParse():
            return ParseResult(result=[], remainder=to_parse)
        remaining_results = parser_(result.remainder)
        return ParseResult(
            result=[result.result] + remaining_results.result,
            remainder=remaining_results.remainder,
        )

    return parser_


@dataclass(frozen=True)
class Skipped:
    pass


def skip(characters: str) -> Parser[Skipped]:
    def parser(to_parse: str) -> ParseResult[Skipped]:
        if any(to_parse.startswith(c) for c in characters):
            return ParseResult(result=Skipped(), remainder=to_parse[1:])
        return ParseResult(result=CouldNotParse(), remainder=to_parse)
    return parser


def word(word_to_parse: str) -> Parser[str]:
    def parser(to_parse: str) -> ParseResult[str]:
        if to_parse.startswith(word_to_parse):
            return ParseResult(result=to_parse[:len(word_to_parse)], remainder=to_parse[len(word_to_parse):])
        return ParseResult(result=CouldNotParse(), remainder=to_parse)
    return parser


S = TypeVar('S')
U = TypeVar('U')


def and_(left_parser: Parser[T], right_parser: Parser[S], combiner: Callable[[S, T], U]) -> Parser[U]:
    def parser(to_parse: str) -> ParseResult[U]:
        result1 = left_parser(to_parse)
        if result1.result == CouldNotParse():
            return ParseResult(result=CouldNotParse(), remainder=to_parse)

        result2 = right_parser(result1.remainder)
        if result2.result == CouldNotParse():
            return ParseResult(result=CouldNotParse(), remainder=to_parse)

        return ParseResult(combiner(result1.result, result2.result),result2.remainder)

    return parser


def right(left_parser: Parser[T], right_parser: Parser[S]) -> Parser[S]:
    return and_(
        left_parser,
        right_parser,
        combiner=lambda t, s: s,
    )


def left(left_parser: Parser[T], right_parser: Parser[S]) -> Parser[T]:
    return and_(
        left_parser,
        right_parser,
        combiner=lambda t, s: t,
    )


def apply(
    function: Callable[[T], S],
    parser: Parser[T], 
) -> Parser[S]:
    def parser_(to_parse: str) -> ParseResult[S]:
        result = parser(to_parse)
        if result.result == CouldNotParse():
            return ParseResult(result=CouldNotParse(), remainder=to_parse)
        return ParseResult(result=function(result.result), remainder=result.remainder)
    return parser_

@dataclass(frozen=True)
class Game:
    id_: int
    bags: list[BagContent]

    @classmethod
    def from_integer_and_bags(cls, integer: int, contents: list[BagContent]) -> Game:
        return Game(integer, contents)



# (Game.from_integer . int) <$> ('Game ' *> digit <* ':')


def separated_by(parser: Parser[T], separator: str) -> Parser[list[T]]:
    return and_(
        many(left(parser, word(separator))),
        parser,
        combiner=lambda ts, t: ts + [t],
    )

@dataclass(frozen=True)
class BagContent:
    red: int = 0
    blue: int = 0
    green: int = 0

    @classmethod
    def from_int_and_str(cls, integer, string) -> BagContent:
        if string == 'red':
            return BagContent(red=integer)
        if string == 'blue':
            return BagContent(blue=integer)
        if string == 'green':
            return BagContent(green=integer)
        raise Exception



def sum_bags(bags: list[BagContent]) -> BagContent:
    red = sum(bag.red for bag in bags)
    blue = sum(bag.blue for bag in bags)
    green = sum(bag.green for bag in bags)
    return BagContent(red=red, blue=blue, green=green)

game_id = apply(
    int, 
    left(
        right(word('Game '), digit), 
        word(': '),
    )
)


integer = apply(
    int, 
    apply(''.join, many(digit))
)
blue = word('blue')
green = word('green')
red = word('red')
color = or_(blue, green, red)
bag_content = and_(
    left(integer, word(' ')), 
    color, 
    combiner=BagContent.from_int_and_str,
)

bag_contents = apply(sum_bags, separated_by(bag_content, ', '))
bag_contentss = separated_by(bag_contents, '; ')

game = and_(game_id, bag_contentss, combiner=Game.from_integer_and_bags)




"""
Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green
"""

print(game_id('Game 1: '))
print(bag_content('3 green'))
print(bag_contentss('3 green, 5 blue; 2 red'))
print(game('Game 1: 3 green, 5 blue; 20 red'))


