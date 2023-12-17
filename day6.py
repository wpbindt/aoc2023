import math
from typing import Iterable

from parsing import *
from dataclasses import dataclass
example_data = """Time:      7  15   30
Distance:  9  40  200
"""


@dataclass(frozen=True)
class RaceParams:
    time_given: int
    distance_to_beat: int


def create_race_params(
    time_given: int,
    distance_to_beat: int,
) -> RaceParams:
    return RaceParams(time_given, distance_to_beat)


def ceil_without_edge(my_float: float) -> int:
    ceiled = math.ceil(my_float)
    if my_float == ceiled:
        return ceiled + 1
    return ceiled


def floor_without_edge(my_float: float) -> int:
    floored = math.floor(my_float)
    if my_float == floored:
        return floored - 1
    return floored


def ways_to_win(race_params: RaceParams) -> int:
    lower_bound = max(
        (race_params.time_given - math.sqrt(race_params.time_given ** 2 - 4 * race_params.distance_to_beat))/2,
        0,
    )
    upper_bound = min((race_params.time_given + math.sqrt(race_params.time_given ** 2 - 4 * race_params.distance_to_beat))/2, race_params.time_given)
    result = 1 + floor_without_edge(upper_bound) - ceil_without_edge(lower_bound)
    return result


def main(data: str) -> int:
    race_params = document(data).result
    assert not isinstance(race_params, CouldNotParse)
    res = 1
    for race_param in race_params:
        res *= ways_to_win(race_param)
    return res



def zipwith(function: Callable[[T, S], U]) -> Callable[[Iterable[T], Iterable[S]], Iterable[U]]:
    def zipper(ts: Iterable[T], ss: Iterable[S]) -> Iterable[U]:
        for t, s in zip(ts, ss):
            yield function(t, s)
    return zipper


whitespace = many_plus(word(' '))

values = separated_by_(integer, whitespace)
time_header = right(word('Time:'), whitespace)
distance_header = right(word('Distance:'), whitespace)
times = right(time_header, values)
distances = right(distance_header, values)
document = and_(times, right(word('\n'), distances), zipwith(create_race_params))


assert whitespace('   ').result == [' ', ' ', ' ']
assert times('Time:   9  10 11').result == [9, 10, 11]
assert distances('Distance:   9  10 11').result == [9, 10, 11]
assert set(document('Time:    1 2 3\nDistance: 4 5  6').result) == {
    RaceParams(1, 4), RaceParams(2, 5), RaceParams(3, 6)
}


assert main(example_data) == 4 * 8 * 9, main(example_data)
