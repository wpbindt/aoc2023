from ast import literal_eval
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
