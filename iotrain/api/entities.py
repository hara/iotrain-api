from enum import Enum


class Direction(Enum):
    STOP = 0
    FORWARD = 1
    BACKWARD = 2


class Speed:
    def __init__(self, value: int):
        if not (0 <= value <= 100):
            raise ValueError("speed_percentage must be between 0 and 100")
        self._value = value

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return "<Speed: {value}>".format(value=self.value)

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if other is None or not isinstance(other, Speed):
            return False
        return self.value == other.value


class Locomotive:
    def __init__(self):
        self.direction = Direction.STOP
        self.speed = Speed(0)

    def operate(self, direction: Direction, speed: Speed):
        self.direction = direction
        self.speed = speed
