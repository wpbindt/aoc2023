from __future__ import annotations
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
