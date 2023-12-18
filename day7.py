from __future__ import annotations

import time
from collections import Counter
from enum import Enum
from functools import cached_property
from itertools import count

from parsing import *
from dataclasses import dataclass

example_data = "32T3K 765\nT55J5 684\nKK677 28\nKTJJT 220\nQQQJA 483"


class HandType(Enum):
    FIVE = 9
    FOUR = 8
    FULL_HOUSE = 7
    THREE = 6
    TWO = 5
    ONE = 4
    HIGH = 3
    OTHER = 0

    def __le__(self, other: HandType) -> bool:
        return self.value <= other.value


@dataclass(frozen=True)
class Line:
    cards: Hand
    bid: int


@dataclass(frozen=True)
class Hand:
    cards: tuple[Card, ...]

    def __post_init__(self) -> None:
        assert len(self.cards) == 5, self.cards

    @cached_property
    def _card_counts(self) -> Counter[int]:
        return Counter(Counter(self.cards).values())

    @cached_property
    def _non_joker_card_counts(self) -> Counter[int]:
        return Counter(Counter([card for card in self.cards if card != Card.J]).values())

    @cached_property
    def type(self) -> HandType:
        if self._card_counts == {5: 1} or self._non_joker_card_counts == {4: 1}:
            return HandType.FIVE
        if self._card_counts == {4: 1, 1: 1}:
            return HandType.FOUR
        if self._card_counts == {2: 1, 3: 1}:
            return HandType.FULL_HOUSE
        if 3 in self._card_counts:
            return HandType.THREE
        if self._card_counts == {2: 2, 1: 1}:
            return HandType.TWO
        if self._card_counts == {2: 1, 1: 3}:
            return HandType.ONE
        return HandType.HIGH

    def __le__(self, other: Hand) -> bool:
        if self.type == other.type:
            return self.cards <= other.cards
        return self.type <= other.type

    def __lt__(self, other: Hand) -> bool:
        return self <= other and self != other


class Card(Enum):
    J = -1
    TWO = 0
    THREE = 1
    FOUR = 2
    FIVE = 3
    SIX = 4
    SEVEN = 5
    EIGHT = 6
    NINE = 7
    T = 8
    Q = 10
    K = 11
    A = 12

    @classmethod
    def from_string(cls, string: str) -> Card:

        if string.isdigit():
            return digits_list[int(string) - 2]
        return Card[string]

    def __le__(self, other: Card) -> bool:
        return self.value <= other.value


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


def main_parsed(hands: list[Line]) -> int:
    sorted_hands = sorted(hands, key=lambda hand: hand.cards)
    return sum(
        rank * line.bid
        for rank, line in zip(count(1), sorted_hands)
    )


def main(to_parse: str) -> int:
    lines = to_parse.split('\n')
    return main_parsed(
        [
            line(line_).result
            for line_ in lines
        ]
    )


assert card('A').result == Card.A
assert card('K').result == Card.K
assert card('3').result == Card.THREE
assert card('4').result == Card.FOUR

assert hand('AAAAA').result == Hand(5 * (Card.A,))

assert line('AAAAA 199').result == Line(Hand(5 * (Card.A,)), bid=199)

five_of_a_kind = Hand(5 * (Card.A,))
four_of_a_kind = Hand((Card.A, Card.A, Card.A, Card.A, Card.K))
four_of_a_kind_different_order = Hand((Card.K, Card.A, Card.A, Card.A, Card.A))
three_of_a_kind = Hand((Card.A, Card.A, Card.A, Card.Q, Card.K))
two_pair = Hand((Card.A, Card.A, Card.Q, Card.Q, Card.K))
one_pair = Hand((Card.A, Card.A, Card.J, Card.Q, Card.K))
high_card = Hand((Card.A, Card.T, Card.J, Card.Q, Card.K))
full_house = Hand((Card.A, Card.A, Card.A, Card.K, Card.K))
assert five_of_a_kind <= five_of_a_kind
assert not five_of_a_kind <= four_of_a_kind
assert four_of_a_kind <= five_of_a_kind
assert full_house <= four_of_a_kind
assert not four_of_a_kind <= full_house
assert three_of_a_kind <= full_house
assert not full_house <= three_of_a_kind
assert two_pair <= three_of_a_kind
assert not three_of_a_kind <= two_pair
assert one_pair <= two_pair
assert not two_pair <= one_pair
assert high_card <= one_pair
assert not one_pair <= high_card
assert not four_of_a_kind <= four_of_a_kind_different_order

assert Card.J <= Card.TWO
assert Hand((Card.A, Card.A, Card.A, Card.A, Card.J)).type == HandType.FIVE

assert main(example_data) == 5905

with open('day7_input', 'r') as f:
    start = time.perf_counter()
    print(main(f.read()))
    end = time.perf_counter()
    print(end - start)
