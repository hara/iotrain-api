from abc import ABC, abstractclassmethod, abstractmethod

from halalabs.iotrain import exceptions, utils
from halalabs.iotrain.entities import Direction, Speed


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
    def control(self, direction: Direction, speed: Speed):
        pass


class IShadowGateway(ABC):
    @abstractmethod
    def update(self, direction: Direction, speed: Speed):
        pass


class IDriveStartInputPort(ABC):
    @abstractmethod
    def execute(self):
        pass


class DriveStartOutputData:
    def __init__(self, direction: Direction, speed: Speed):
        self.direction = direction
        self.speed = speed


class DriveStartInteractor(IDriveStartInputPort):
    def __init__(self, context: IDriveContext, shadow_gateway: IShadowGateway):
        self.context = context
        self.shadow_gateway = shadow_gateway

    @utils.logging
    def execute(self):
        self.shadow_gateway.update(self.context.drive.current_state.direction,
                                   self.context.drive.current_state.speed)


class DriveOperateInputData(InputData):
    def __init__(self, direction: Direction = None, speed: Speed = None):
        self.direction = direction
        self.speed = speed

    def __str__(self):
        return '{class_}(direction={direction}, speed={speed})'.format(
            class_=self.__class__.__name__,
            direction=self.direction,
            speed=self.speed)

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
                    'direction must be STOP or FORWARD or BACKWARD')
        speed = None
        if dict_.get('speed'):
            if isinstance(dict_['speed'], int) and 0 <= dict_['speed'] <= 100:
                speed = Speed(dict_['speed'])
            else:
                invalid.add_error('speed must be integer between 0 and 100')

        if direction is None and speed is None:
            invalid.add_error('direction or speed must be specified')

        if invalid.has_errors():
            return invalid

        return DriveOperateInputData(direction, speed)


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

        if self.context.drive.operate(input.direction, input.speed):
            self.motor_gateway.control(
                self.context.drive.current_state.direction,
                self.context.drive.current_state.speed)
            self.shadow_gateway.update(input.direction, input.speed)
