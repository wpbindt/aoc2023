def parse_document(lines: list[str]) -> int:
    return sum(parse_line(line) for line in lines if line != '')


def parse_line(line: str) -> int:
    digits = [c for c in line if c in {str(i) for i in range(10)}]
    if len(digits) == 0:
        return 0
    return int(digits[0] + digits[-1])



assert parse_line('12') == 12
assert parse_line('1a3') == 13
assert parse_line('b3a8') == 38
assert parse_document(['b2c9', '1234']) == 29 + 14
assert parse_document(['b2c9', '', '1234']) == 29 + 14
assert parse_document(['b2c9', '\n', '1234']) == 29 + 14


with open('day1_input', 'r') as f:
    lines = [line for line in f]

print(parse_document(lines))
