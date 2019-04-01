from unittest.mock import patch

import pytest

from halalabs.iotrain import controllers, entities, usecases


class MockLocomotiveOperateInputPort(usecases.ILocomotiveOperateInputPort):
    def execute(self, input: dict):
        pass


@pytest.fixture
def operate():
    return MockLocomotiveOperateInputPort()


class TestLocomotiveController:
    def test_operate(self, operate):
        controller = controllers.LocomotiveController(operate)
        with patch.object(operate, 'execute') as execute:
            input = {'direction': 'FORWARD', 'speed': 10}
            controller.operate(input)
            assert execute.call_args[0][
                0].direction == entities.Direction.FORWARD
            assert execute.call_args[0][0].speed == entities.Speed(10)
