from uuid import uuid4
from dataclasses import dataclass
from enum import Enum, auto
from typing import Union, Iterator, Generic, Protocol, TypeVar
import string


class Digit(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9


def parse_document(lines: list[str]) -> int:
    return sum(
        int(str(parsed_line[0].value) + str(parsed_line[-1].value))
        for parsed_line in map(parse_line, lines)
        if len(parsed_line) > 0
    )


def parse_line(line: str) -> list[Digit]:
    tokens = many(
            or_(
                parse_digit, 
                skip(string.ascii_lowercase)))(line).result
    return [token for token in tokens if token != Skipped()]


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
        if to_parse.startswith(result.name.lower()):
            return ParseResult(remainder=to_parse[len(result.name):], result=result)
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

assert skip('b')('b').remainder == ''
assert skip('b')('bcd').remainder == 'cd'

assert parse_line('12') == [Digit.ONE, Digit.TWO]
assert parse_line('1a3') == [Digit.ONE, Digit.THREE], parse_line('1a3')
assert parse_line('b3a8') == [Digit.THREE, Digit.EIGHT]
assert parse_line('b2c9') == [Digit.TWO, Digit.NINE]

assert parse_document(['b2c9', '1234']) == 29 + 14, parse_document(['b2c9', '1234']) 
assert parse_document(['b2c9', '', '1234']) == 29 + 14
assert parse_document(['b2c9', '\n', '1234']) == 29 + 14
assert parse_document(['onetwo', '3afour', 'afive6', 'a7b8c']) == 12 + 34 + 56 + 78
assert parse_document(['2', '1']) == 33
assert parse_document(['a2', '1']) == 33
assert parse_document(['aaa', '1']) == 11
assert parse_document(['a3a2aaaaaa2', 'as2a1a1\n', '\n']) == 53
assert parse_document(['sevennine']) == 79
assert parse_document(['sevenine']) in {77, 99}
assert parse_document(['1nineight']) in {19, 18}
assert parse_document(['sevenineight']) == 78


d = {
    'vvcfdjlpcrfnnmbcx4eight9mtcfqqqfl5fourfive': 45,
    'qbcxpccssl9kvqtjncjdxsrpp8sixbnmq': 96,
    'sixonexjgqthdnrpfivetgnxqv1': 61,
    'eightthree33ngpkqtqgtkmcfgqqgj313': 83,
    'onezfnlseven1': 11,
    '2threefhcs': 23,
    '3nineeightzmpvjqrvcb1tkmchzjtsrfllv': 31,
    '58cjnxhzfknnkj4ninezvskrvrc': 59,
    'hthree16zdtbfnlx': 36,
    'tzqcksevenfour3foursix5': 75,
    'qbbzz1threesevenone': 11,
    'onegfzhlthree12': 12,
    'gpjjzfiveone21qbrjdrz7': 57,
    'xcpjznj54fivesevenfiveq': 55,
    'gsevenflcgfcmqtrzstrmnine9two': 72,
    '7nrsmkbqffnnvfpjgb': 77,
    'tfhnnmpbzq67six': 66,
    '52jhltfzqhfprmtgbmhg': 52,
    'vchpblqmsvffourzkndtsg7': 47,
    'eightsevenvgfpttr62hmfzf4f': 84,
    'eight4four1tsvfq': 81,
    '4sevensix': 46,
    'vrkmjrrxnbgjbxfqxllp17four1bdm6': 16,
    '2kqfd4threefour5': 25,
    '44m': 44,
    '3four2zcfvtplkrbeight274': 34,
    'one7sixninesix': 16,
    'kkxmtmdthree6jrj6': 36,
    '81sevenmnine1llbqrsprc': 81,
    '5nine9qgjceight': 58,
    'three1sdmq9sevenfournine': 39,
    'khnlbmzhvlsix3': 63,
    'nineone6onesixvlnlxeightfive': 95,
    'schplznseveneightnlcxgr7four': 74,
    '6one1djcdmpdrgq3two': 62,
    'fourzhpnphmq52r813four': 44,
    'scsxjthreefoureight2fivepfmpfj8': 38,
    '69xvbxfffmr7one8gmch8': 68,
    'one8tfpgrdhm': 18,
    '2gxmhtfrbrkpdvlvsmdqrktxtrpssbrv933': 23,
    '4vfrtkdqlbtwordlbppsssp': 42,
    '2cjmtvnzpbkdcq5twofourtwo': 22,
    '2three5onetwogpfqtszbjh': 22,
    'hgvnine9four996': 96,
    '37142745': 35,
    'four73': 43,
    '8552ztclnd': 82,
    'onevmpd76eighth': 18,
    'threethree8': 38,
    'bgtwoonedrmc35': 25,
    '23one': 21,
    '9lpxzhkck2five3qone9zgxzrzd': 99,
    'hs1': 11,
}


print(uuid4())
assert parse_document(list(d.keys())) == sum(d.values())


with open('day1_input', 'r') as f:
    lines = [
        line
        .rstrip()
        .replace('one', 'oonee')
        .replace('two', 'ttwoo')
        for line in f
    ]


assert parse_document(lines) == 55343, parse_document(lines)

