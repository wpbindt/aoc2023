from __future__ import annotations
from enum import Enum, auto
from parsing import *
from dataclasses import dataclass

example_data = """32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483
"""


@dataclass(frozen=True)
class Line:
    cards: Hand
    bid: int


@dataclass(frozen=True)
class Hand:
    cards: tuple[Card, ...]

    def __post_init__(self) -> None:
        assert len(self.cards) == 5

    def is_5_kind(self) -> bool:
        return len(set(self.cards)) == 1

    def __le__(self, other: Hand) -> bool:
        if self.is_5_kind() and not other.is_5_kind():
            return False
        return True


class Card(Enum):
    TWO = 0
    THREE = 1
    FOUR = 2
    FIVE = 3
    SIX = 4
    SEVEN = 5
    EIGHT = 6
    NINE = 7
    T = 8
    J = 9
    Q = 10
    K = 11
    A = 12

    @classmethod
    def from_string(cls, string: str) -> Card:

        if string.isdigit():
            return digits_list[int(string) - 2]
        return Card[string]


digits_list = [
    Card.TWO,
    Card.THREE,
    Card.FOUR,
    Card.FIVE,
    Card.SIX,
    Card.SEVEN,
    Card.EIGHT,
    Card.NINE,
]

card = apply(
    Card.from_string,
    or_(
        word('T'),
        word('J'),
        word('Q'),
        word('K'),
        word('A'),
        digit,
    )
)

hand = apply(lambda cards: Hand(tuple(cards)), many(card))
bid = integer
line = and_(hand, right(word(' '), bid), lambda h, b: Line(h, b))
lines = separated_by(line, '\n')


def main(to_parse: str) -> int:
    pass


assert card('A').result == Card.A
assert card('K').result == Card.K
assert card('3').result == Card.THREE
assert card('4').result == Card.FOUR

assert hand('AAAAA').result == Hand(5 * (Card.A,))

assert line('AAAAA 199').result == Line(Hand(5 * (Card.A,)), bid=199)

assert lines('AAAAA 199\n22222 1').result == [Line(Hand(5 * (Card.A,)), bid=199), Line(Hand(5 * (Card.TWO,)), 1)]

assert Hand(5 * (Card.A,)) <= Hand(5 * (Card.A,))
assert not (Hand(5 * (Card.A,)) <= Hand((Card.A, Card.A, Card.A, Card.A, Card.K)))

assert main(example_data) == 6440
