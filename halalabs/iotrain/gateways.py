import json

from halalabs.iotrain import utils
from halalabs.iotrain.entities import Direction, ThrottlePercentage
from halalabs.iotrain.usecases import IMotorGateway, IShadowGateway


class MotorGateway(IMotorGateway):
    def __init__(self, motor):
        self.motor = motor

    @utils.logging
    def control(self, direction: Direction, throttle: ThrottlePercentage):
        if direction == Direction.NEUTRAL:
            self.motor.speed(0)
        elif direction == Direction.FORWARD:
            self.motor.speed(throttle.value)
        elif direction == Direction.REVERSE:
            self.motor.speed(throttle.value * -1)


class ShadowGateway(IShadowGateway):
    def __init__(self, shadow):
        self.shadow = shadow

    @utils.logging
    def _update_callback(self, payload, responseStatus, token):
        pass

    @utils.logging
    def update(self,
               direction: Direction = None,
               throttle: ThrottlePercentage = None):
        payload = {'state': {'reported': {}}}
        if direction is not None:
            payload['state']['reported']['direction'] = direction.name
        if throttle is not None:
            payload['state']['reported']['throttle'] = throttle.value
        if payload['state']['reported']:
            self.shadow.shadowUpdate(
                json.dumps(payload), self._update_callback, 5)
