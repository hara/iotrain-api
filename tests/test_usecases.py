from unittest.mock import MagicMock

import pytest

from iotrain.api import exceptions, usecases


@pytest.fixture
def locomotive():
    return MagicMock()


@pytest.fixture
def motor_gateway():
    return MagicMock()


class TestInvalidInputData:
    def test_add_error(self):
        input_data = usecases.InvalidInputData()
        input_data.add_error('error1')
        assert input_data.errors[0] == 'error1'
        input_data.add_error('error2')
        assert input_data.errors[1] == 'error2'

    def test_has_errors(self):
        input_data = usecases.InvalidInputData()
        assert not input_data.has_errors()
        input_data.add_error('error')
        assert input_data.has_errors()

    def test_is_false(self):
        input_data = usecases.InvalidInputData()
        assert not input_data


class TestLocomotiveOperateInputData:
    def test_from_dict(self):
        input_dict = {'direction': 'FORWARD', 'speed': 10}
        input_data = usecases.LocomotiveOperateInputData.from_dict(input_dict)
        assert input_data.direction == usecases.Direction.FORWARD
        assert input_data.speed == usecases.Speed(10)

    def test_invalid_direction(self):
        input_dict = {'direction': 'INVALID', 'speed': 10}
        input_data = usecases.LocomotiveOperateInputData.from_dict(input_dict)
        assert not input_data
        assert input_data.errors[
            0] == 'direction must be STOP or FORWARD or BACKWARD'

    def test_invalid_speed(self):
        error = 'speed must be integer between 0 and 100'

        input_dict = {'direction': 'FORWARD', 'speed': -1}
        input_data = usecases.LocomotiveOperateInputData.from_dict(input_dict)
        assert not input_data
        assert input_data.errors[0] == error

        input_dict = {'direction': 'FORWARD', 'speed': 101}
        input_data = usecases.LocomotiveOperateInputData.from_dict(input_dict)
        assert not input_data
        assert input_data.errors[0] == error

        input_dict = {'direction': 'FORWARD', 'speed': '1'}
        input_data = usecases.LocomotiveOperateInputData.from_dict(input_dict)
        assert not input_data
        assert input_data.errors[0] == error


class TestLocomotiveOperateInteractor:
    def test_operate(self, locomotive, motor_gateway):
        interactor = usecases.LocomotiveOperateInteractor(
            locomotive, motor_gateway)

        input_dict = {'direction': 'FORWARD', 'speed': 10}
        input_data = usecases.LocomotiveOperateInputData.from_dict(input_dict)
        interactor.execute(input_data)
        assert locomotive.operate.call_args[0] == (input_data.direction,
                                                   input_data.speed)
        assert motor_gateway.control.call_args[0] == (input_data.direction,
                                                      input_data.speed)

    def test_operation_error(self, locomotive, motor_gateway):
        interactor = usecases.LocomotiveOperateInteractor(
            locomotive, motor_gateway)

        input_dict = {'direction': 'FORWARD'}
        input_data = usecases.LocomotiveOperateInputData.from_dict(input_dict)
        with pytest.raises(exceptions.LocomotiveOperationError):
            interactor.execute(input_data)

        input_dict = {'speed': 10}
        input_data = usecases.LocomotiveOperateInputData.from_dict(input_dict)
        with pytest.raises(exceptions.LocomotiveOperationError):
            interactor.execute(input_data)

        input_dict = {}
        input_data = usecases.LocomotiveOperateInputData.from_dict(input_dict)
        with pytest.raises(exceptions.LocomotiveOperationError):
            interactor.execute(input_data)
