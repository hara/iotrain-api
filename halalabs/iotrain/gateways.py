from halalabs.iotrain import utils
from halalabs.iotrain.entities import Direction, Speed
from halalabs.iotrain.usecases import IMotorGateway


class MotorGateway(IMotorGateway):
    def __init__(self, motor):
        self.motor = motor

    @utils.logging
    def control(self, direction: Direction, speed: Speed):
        if direction == Direction.STOP:
            self.motor.speed(0)
        elif direction == Direction.FORWARD:
            self.motor.speed(speed.value)
        elif direction == Direction.BACKWARD:
            self.motor.speed(speed.value * -1)
