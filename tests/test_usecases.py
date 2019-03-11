from unittest.mock import MagicMock, patch

import pytest

from halalabs.iotrain import entities, exceptions, usecases
from halalabs.iotrain.context import DriveContext


@pytest.fixture
def drive_context():
    return DriveContext(entities.Drive())


@pytest.fixture
def shadow_gateway():
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


class TestDriveOperateInputData:
    def test_from_dict(self):
        input_dict = {'direction': 'FORWARD'}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        assert input_data.direction == usecases.Direction.FORWARD
        assert input_data.speed is None

        input_dict = {'speed': 10}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        assert input_data.direction is None
        assert input_data.speed == usecases.Speed(10)

        input_dict = {'direction': 'FORWARD', 'speed': 10}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        assert input_data.direction == usecases.Direction.FORWARD
        assert input_data.speed == usecases.Speed(10)

    def test_invalid_direction(self):
        input_dict = {'direction': 'BACKWARD'}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        assert not input_data
        assert input_data.errors[
            0] == 'direction must be NEUTRAL or FORWARD or REVERSE'

    def test_invalid_speed(self):
        input_dict = {'speed': '1'}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        assert not input_data
        assert input_data.errors[
            0] == 'speed must be integer between 0 and 100'

        input_dict = {'speed': 101}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        assert not input_data
        assert input_data.errors[
            0] == 'speed must be integer between 0 and 100'

    def test_no_operation(self):
        input_dict = {}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        assert not input_data
        assert input_data.errors[0] == 'direction or speed must be specified'


class TestDriveOperateInteractor:
    def test_operate(self, drive_context, motor_gateway, shadow_gateway):
        interactor = usecases.DriveOperateInteractor(
            drive_context, motor_gateway, shadow_gateway)

        input_dict = {'direction': 'FORWARD', 'speed': 10}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        with patch.object(drive_context.drive, 'operate') as operate:
            interactor.execute(input_data)
            assert operate.call_args[0] == (input_data.direction,
                                            input_data.speed)

        input_dict = {'direction': 'REVERSE'}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        with patch.object(drive_context.drive, 'operate') as operate:
            interactor.execute(input_data)
            assert operate.call_args[0] == (input_data.direction, None)

        input_dict = {'speed': 20}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        with patch.object(drive_context.drive, 'operate') as operate:
            interactor.execute(input_data)
            assert operate.call_args[0] == (None, input_data.speed)

    def test_not_operate(self, drive_context, motor_gateway, shadow_gateway):
        interactor = usecases.DriveOperateInteractor(
            drive_context, motor_gateway, shadow_gateway)

        input_dict = {'direction': 'FORWARD', 'speed': 10}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        with patch.object(drive_context.drive, 'operate') as operate:
            interactor.execute(input_data)
            assert len(operate.call_args_list) == 1

        input_dict = {'direction': 'FORWARD', 'speed': 10}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        with patch.object(drive_context.drive, 'operate') as operate:
            interactor.execute(input_data)
            assert len(operate.call_args_list) == 1

    def test_control_motor(self, drive_context, motor_gateway, shadow_gateway):
        interactor = usecases.DriveOperateInteractor(
            drive_context, motor_gateway, shadow_gateway)

        input_dict = {'direction': 'FORWARD', 'speed': 10}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        interactor.execute(input_data)
        assert motor_gateway.control.call_args[0] == (input_data.direction,
                                                      input_data.speed)

        input_dict = {'direction': 'REVERSE'}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        interactor.execute(input_data)
        assert motor_gateway.control.call_args[0] == (
            input_data.direction, drive_context.drive.current_state.speed)

        input_dict = {'speed': 20}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        interactor.execute(input_data)
        assert motor_gateway.control.call_args[0] == (
            drive_context.drive.current_state.direction, input_data.speed)

    def test_not_control_motor(self, drive_context, motor_gateway,
                               shadow_gateway):
        interactor = usecases.DriveOperateInteractor(
            drive_context, motor_gateway, shadow_gateway)

        input_dict = {'direction': 'FORWARD', 'speed': 10}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        interactor.execute(input_data)
        assert len(motor_gateway.control.call_args_list) == 1

        input_dict = {'direction': 'FORWARD', 'speed': 10}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        interactor.execute(input_data)
        assert len(motor_gateway.control.call_args_list) == 1

    def test_update_shadow(self, drive_context, motor_gateway, shadow_gateway):
        interactor = usecases.DriveOperateInteractor(
            drive_context, motor_gateway, shadow_gateway)

        input_dict = {'direction': 'FORWARD', 'speed': 10}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        interactor.execute(input_data)
        assert shadow_gateway.update.call_args[0] == (input_data.direction,
                                                      input_data.speed)

        input_dict = {'direction': 'REVERSE'}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        interactor.execute(input_data)
        assert shadow_gateway.update.call_args[0] == (input_data.direction,
                                                      None)

        input_dict = {'speed': 20}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        interactor.execute(input_data)
        assert shadow_gateway.update.call_args[0] == (None, input_data.speed)

    def test_not_update_shadow(self, drive_context, motor_gateway,
                               shadow_gateway):
        interactor = usecases.DriveOperateInteractor(
            drive_context, motor_gateway, shadow_gateway)

        input_dict = {'direction': 'FORWARD', 'speed': 10}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        interactor.execute(input_data)
        assert len(shadow_gateway.update.call_args_list) == 1

        input_dict = {'direction': 'FORWARD', 'speed': 10}
        input_data = usecases.DriveOperateInputData.from_dict(input_dict)
        interactor.execute(input_data)
        assert len(shadow_gateway.update.call_args_list) == 1

    def test_no_operation(self, drive_context, motor_gateway, shadow_gateway):
        input_data = usecases.DriveOperateInputData.from_dict({})

        interactor = usecases.DriveOperateInteractor(
            drive_context, motor_gateway, shadow_gateway)
        with pytest.raises(exceptions.DriveOperationError):
            interactor.execute(input_data)
