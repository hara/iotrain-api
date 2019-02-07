from unittest.mock import patch

import pytest

from halalabs.iotrain import controllers, entities, usecases


class MockDriveStartInputPort(usecases.IDriveStartInputPort):
    def execute(self):
        pass


class MockDriveOperateInputPort(usecases.IDriveOperateInputPort):
    def execute(self, input: dict):
        pass


@pytest.fixture
def start():
    return MockDriveStartInputPort()


@pytest.fixture
def operate():
    return MockDriveOperateInputPort()


class TestDriveController:
    def test_start(self, start, operate):
        controller = controllers.DriveController(start, operate)
        with patch.object(start, 'execute') as execute:
            controller.start()
            assert execute.called

    def test_operate(self, start, operate):
        controller = controllers.DriveController(start, operate)
        with patch.object(operate, 'execute') as execute:
            input = {'direction': 'FORWARD', 'throttle': 10}
            controller.operate(input)
            assert execute.call_args[0][
                0].direction == entities.Direction.FORWARD
            assert execute.call_args[0][
                0].throttle == entities.ThrottlePercentage(10)
