from iotrain.api import utils
from iotrain.api.entities import Direction, Speed
from iotrain.api.usecases import IMotorGateway


class MotorGateway(IMotorGateway):
    def __init__(self, motor):
        self.motor = motor

    @utils.logging
    def control(self, direction: Direction, speed: Speed):
        if direction == Direction.STOP:
            self.motor.speed(0)
        elif direction == Direction.FORWARD:
            self.motor.speed(speed.value * -1)
        elif direction == Direction.BACKWARD:
            self.motor.speed(speed.value)
