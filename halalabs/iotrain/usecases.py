from abc import ABC, abstractclassmethod, abstractmethod

from halalabs.iotrain import exceptions, utils
from halalabs.iotrain.entities import Direction, ThrottlePercentage


class InputData(ABC):
    @abstractclassmethod
    def from_dict(cls, dict_):
        pass

    def __bool__(self):
        return True


class InvalidInputData:
    def __init__(self):
        self.errors = []

    def add_error(self, error):
        self.errors.append(error)

    def has_errors(self):
        return len(self.errors) > 0

    def __bool__(self):
        return False

    def __str__(self):
        return '{class_}(errors={errors})'.format(
            class_=self.__class__.__name__, errors=self.errors)


class IDriveContext(ABC):
    pass


class IMotorGateway(ABC):
    @abstractmethod
    def control(self, direction: Direction, throttle: ThrottlePercentage):
        pass


class IShadowGateway(ABC):
    @abstractmethod
    def update(self, direction: Direction, throttle: ThrottlePercentage):
        pass


class IDriveStartInputPort(ABC):
    @abstractmethod
    def execute(self):
        pass


class DriveStartOutputData:
    def __init__(self, direction: Direction, throttle: ThrottlePercentage):
        self.direction = direction
        self.throttle = throttle


class DriveStartInteractor(IDriveStartInputPort):
    def __init__(self, context: IDriveContext, shadow_gateway: IShadowGateway):
        self.context = context
        self.shadow_gateway = shadow_gateway

    @utils.logging
    def execute(self):
        self.shadow_gateway.update(self.context.drive.current_state.direction,
                                   self.context.drive.current_state.throttle)


class DriveOperateInputData(InputData):
    def __init__(self,
                 direction: Direction = None,
                 throttle: ThrottlePercentage = None):
        self.direction = direction
        self.throttle = throttle

    def __str__(self):
        return '{class_}(direction={direction}, throttle={throttle})'.format(
            class_=self.__class__.__name__,
            direction=self.direction,
            throttle=self.throttle)

    @classmethod
    @utils.logging
    def from_dict(cls, dict_):
        invalid = InvalidInputData()

        direction = None
        if dict_.get('direction'):
            if dict_['direction'] in [d.name for d in Direction]:
                direction = Direction[dict_['direction']]
            else:
                invalid.add_error(
                    'direction must be NEUTRAL or FORWARD or REVERSE')
        throttle = None
        if dict_.get('throttle'):
            if isinstance(dict_['throttle'],
                          int) and 0 <= dict_['throttle'] <= 100:
                throttle = ThrottlePercentage(dict_['throttle'])
            else:
                invalid.add_error('throttle must be integer between 0 and 100')

        if direction is None and throttle is None:
            invalid.add_error('direction or throttle must be specified')

        if invalid.has_errors():
            return invalid

        return DriveOperateInputData(direction, throttle)


class IDriveOperateInputPort(ABC):
    @abstractmethod
    def execute(self, input: dict):
        pass


class DriveOperateInteractor(IDriveOperateInputPort):
    def __init__(self, context: IDriveContext, motor_gateway: IMotorGateway,
                 shadow_gateway: IShadowGateway):
        self.context = context
        self.motor_gateway = motor_gateway
        self.shadow_gateway = shadow_gateway

    @utils.logging
    def execute(self, input: DriveOperateInputData):
        if not input:
            raise exceptions.DriveOperationError

        if self.context.drive.operate(input.direction, input.throttle):
            self.motor_gateway.control(
                self.context.drive.current_state.direction,
                self.context.drive.current_state.throttle)
            self.shadow_gateway.update(input.direction, input.throttle)
