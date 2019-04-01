from unittest.mock import patch

import pytest

from halalabs.iotrain import controllers, entities, usecases


class MockDriveOperateInputPort(usecases.IDriveOperateInputPort):
    def execute(self, input: dict):
        pass


@pytest.fixture
def operate():
    return MockDriveOperateInputPort()


class TestDriveController:
    def test_operate(self, operate):
        controller = controllers.DriveController(operate)
        with patch.object(operate, 'execute') as execute:
            input = {'direction': 'FORWARD', 'speed': 10}
            controller.operate(input)
            assert execute.call_args[0][
                0].direction == entities.Direction.FORWARD
            assert execute.call_args[0][0].speed == entities.Speed(10)
