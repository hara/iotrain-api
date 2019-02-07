from collections import namedtuple
from datetime import datetime
from enum import Enum
from uuid import uuid4


class Id(namedtuple('Id', 'value')):
    __slots__ = ()

    @classmethod
    def new_id(cls):
        return Id(str(uuid4()))

    def __str__(self):
        return self.value


class Direction(Enum):
    NEUTRAL = 0
    FORWARD = 1
    REVERSE = 2


class ThrottlePercentage:
    def __init__(self, value: int):
        if not (0 <= value <= 100):
            raise ValueError('throttle_percentage must be between 0 and 100')
        self._value = value

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return '<ThrottlePercentage: {value}>'.format(value=self.value)

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if other is None or not isinstance(other, ThrottlePercentage):
            return False
        return self.value == other.value


class DriveState:
    def __init__(self, direction: Direction, throttle: ThrottlePercentage):
        self.id = Id.new_id()
        self.direction = direction
        self.throttle = throttle
        self.reported_at = datetime.now()


class Drive:
    def __init__(self, id: Id = None):
        self.id = id or Id.new_id()
        initial_state = DriveState(Direction.NEUTRAL, ThrottlePercentage(0))
        self.history = [initial_state]
        self.started_at = datetime.now()

    def operate(self,
                direction: Direction = None,
                throttle: ThrottlePercentage = None):
        new_direction = direction or self.current_state.direction
        new_throttle = throttle or self.current_state.throttle
        if (new_direction == self.current_state.direction
                and new_throttle == self.current_state.throttle):
            return False
        state = DriveState(new_direction, new_throttle)
        self.history.append(state)
        return True

    @property
    def current_state(self) -> DriveState:
        return self.history[-1]
