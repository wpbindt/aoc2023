import random
from typing import Callable, Protocol, TypeVar, TypeVarTuple

T = TypeVar('T')



Ts = TypeVarTuple("Ts")


def inject(
    dependency: Callable[[], T],
) -> Callable[
    [Callable[[T, *Ts], None]],
    Callable[[*Ts], None],
]:
    def decorator(
        property_test: Callable[[T, *Ts], None]
    ) -> Callable[[*Ts], None]:
        def curried_test(*remaining_dependencies: *Ts) -> None:
            property_test(dependency(), *remaining_dependencies)
        return curried_test
    return decorator


def run_property_test(property_test: Callable[[], None]) -> None:
    for _ in range(1000):
        print(_)
        property_test()


def multiply(a: int, b: str) -> str:
    return ''


def positive_integer() -> int:
    return random.randint(1, 1000)


def string() -> str:
    return 'random'


@inject(string)
def property_test_multiplying_by_0_gives_empty_string(b: str) -> None:
    assert multiply(0, b) == ''


@inject(positive_integer)
@inject(string)
def property_test_multiplying_by_positive_integer_does_not_lower_length(b: str, a: int) -> None:
    assert len(multiply(a, b)) >= len(b)


if __name__ == '__main__':
    run_property_test(property_test_multiplying_by_0_gives_empty_string)
    run_property_test(property_test_multiplying_by_positive_integer_does_not_lower_length)
