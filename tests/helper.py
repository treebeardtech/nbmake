from typing import Callable, TypeVar

T = TypeVar("T")


class MockValidator(object):
    def __init__(self, validator: Callable[[T], bool]):
        self.validator = validator

    def __eq__(self, other: T):
        return bool(self.validator(other))
