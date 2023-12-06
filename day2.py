from __future__ import annotations
from uuid import uuid4
from dataclasses import dataclass
from typing import Union, Iterator, Generic, Protocol, TypeVar
import string
from parsing import *


T = TypeVar('T')



@dataclass(frozen=True)
class Game:
    id_: int
    bags: list[BagContent]

    @classmethod
    def from_integer_and_bags(cls, integer: int, contents: list[BagContent]) -> Game:
        return Game(integer, contents)

    def is_possible_with(self, bag: BagContent) -> bool:
        if len(self.bags) == 0:
            return False
        return all(revealed_bag <= bag for revealed_bag in self.bags)

    def get_lower_bound(self) -> BagContent:
        return BagContent(
            red=max(bag.red for bag in self.bags),
            blue=max(bag.blue for bag in self.bags),
            green=max(bag.green for bag in self.bags),
        )
        return self.bags[0]


# (Game.from_integer . int) <$> ('Game ' *> digit <* ':')



@dataclass(frozen=True)
class BagContent:
    red: int = 0
    blue: int = 0
    green: int = 0

    def power(self) -> int:
        return self.red * self.blue * self.green

    @classmethod
    def from_int_and_str(cls, integer, string) -> BagContent:
        if string == 'red':
            return BagContent(red=integer)
        if string == 'blue':
            return BagContent(blue=integer)
        if string == 'green':
            return BagContent(green=integer)
        raise Exception

    def __le__(self, other):
        return self.red <= other.red and self.blue <= other.blue and self.green <= other.green



def sum_bags(bags: list[BagContent]) -> BagContent:
    red = sum(bag.red for bag in bags)
    blue = sum(bag.blue for bag in bags)
    green = sum(bag.green for bag in bags)
    return BagContent(red=red, blue=blue, green=green)

integer = apply(
    int, 
    apply(''.join, many(digit))
)

game_id = left(
    right(word('Game '), integer), 
    word(': '),
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


def collect_possible_games(unparsed_games: list[str], bag: BagContent) -> int:
    games = [game(unparsed_game).result for unparsed_game in unparsed_games]
    return sum(game.id_ for game in games if game.is_possible_with(bag))


def sum_powers(unparsed_games: list[str]) -> int:
    games = [game(unparsed_game).result for unparsed_game in unparsed_games]
    return sum(game.get_lower_bound().power() for game in games)

assert not Game(id_=1, bags=[]).is_possible_with(BagContent(1, 2, 3))
assert not Game(id_=1, bags=[BagContent(12, 2, 3)]).is_possible_with(BagContent(1, 2, 3))
assert collect_possible_games(
    [
        "Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green",
        "Game 2: 9 blue, 4 red; 1 red, 2 green, 6 blue; 2 green",
    ],
    BagContent(blue=8, red=100, green=100)
) == 1
assert Game(id_=1, bags=[BagContent(12, 2, 3)]).get_lower_bound() == BagContent(12, 2, 3)
assert Game(
    id_=1, 
    bags=[
        BagContent(12, 2, 3),
        BagContent(11, 4, 3),
    ]
).get_lower_bound() == BagContent(12, 4, 3)
assert BagContent(12, 2, 3).power() == 12 * 2 * 3

assert sum_powers(
    [
        "Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green",  # 4 
        "Game 2: 9 blue, 4 red; 1 red, 2 green, 6 blue; 2 green",
    ],
) == 4 * 6 * 2 + 9 * 4 * 2

with open('day2_input', 'r') as f:
    unparsed_games = [line for line in f]

print(sum_powers(unparsed_games))

