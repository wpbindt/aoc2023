from ast import literal_eval
from math import lcm
from typing import Iterator
from itertools import cycle, count

with open('day8_input') as f:
    instructions, map_ = literal_eval(f.read())

instructions = instructions.replace('L', '0').replace('R', '1')
current = 'AAA'
for score, instruction in zip(count(1), cycle(instructions)):
    current = map_[current][int(instruction)]
    if current == 'ZZZ':
        print(score)
        break

starting_points = [x for x in map_ if x.endswith('A')]
print(starting_points)


def traverse(starting_point: str) -> Iterator[str]:
    current = starting_point
    for instruction in cycle(instructions):
        current = map_[current][int(instruction)]
        yield current


def detect_cycle(starting_node):
    last_score = 0
    previous_difference = 0
    for score, node in zip(count(1), traverse(starting_node)):
        if node.endswith('Z'):
            difference = score - last_score
            print(f'{score=}')
            print(score - last_score)
            last_score = score
            if difference == previous_difference:
                return difference
            previous_difference = difference


traversals = map(traverse, starting_points)
bops = []
for node in starting_points:
    print(node)
    bops.append(detect_cycle(node))

print(bops)
print(lcm(*bops))
# for score, *itineraries in zip(count(1), *traversals):
#     if all(node.endswith('Z') for node in itineraries):
#         print(score)
#         break
