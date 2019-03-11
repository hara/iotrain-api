import re
from datetime import datetime

import freezegun
import pytest

from halalabs.iotrain import entities

UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}")


class TestId:
    def test_equality(self):
        assert entities.Id('a') == entities.Id('a')
        assert entities.Id('a') != entities.Id('b')

    def test_str(self):
        id = entities.Id.new_id()
        assert str(id) == id.value

    def test_new_id(self):
        id = entities.Id.new_id()
        assert UUID_PATTERN.match(id.value)


class TestSpeed:
    @pytest.mark.parametrize("value", [0, 1, 99, 100])
    def test_valid_percentage(self, value):
        percentage = entities.Speed(value)
        assert percentage.value == value

    @pytest.mark.parametrize("value", [-1, 101])
    def test_invalid_percentage(self, value):
        with pytest.raises(ValueError):
            entities.Speed(value)

    def test_equality(self):
        assert entities.Speed(0) == entities.Speed(0)
        assert entities.Speed(0) != entities.Speed(1)
        assert entities.Speed(0) != 0

    def test_str(self):
        assert str(entities.Speed(0)) == '0'

    def test_repr(self):
        assert repr(entities.Speed(0)) == '<Speed: 0>'


class TestDriveState:
    def test_initialize(self):
        state = entities.DriveState(entities.Direction.NEUTRAL,
                                    entities.Speed(0))
        assert UUID_PATTERN.match(state.id.value)
        assert state.direction == entities.Direction.NEUTRAL
        assert state.speed == entities.Speed(0)


class TestDrive:
    def test_init(self):
        now = datetime(2019, 2, 3)
        with freezegun.freeze_time(now):
            drive = entities.Drive()
            assert UUID_PATTERN.match(drive.id.value)
            assert drive.started_at == now
            assert len(drive.history) == 1
            assert drive.history[0].direction == entities.Direction.NEUTRAL
            assert drive.history[0].speed == entities.Speed(0)

    def test_initial_state(self):
        drive = entities.Drive()
        state = drive.current_state
        assert state.direction == entities.Direction.NEUTRAL
        assert state.speed == entities.Speed(0)

    def test_operate(self):
        drive = entities.Drive()

        state = drive.current_state
        assert drive.operate(direction=entities.Direction.REVERSE)
        assert drive.current_state != state
        assert drive.current_state.direction == entities.Direction.REVERSE
        assert drive.current_state.speed == entities.Speed(0)

        state = drive.current_state
        assert drive.operate(speed=entities.Speed(10))
        assert drive.current_state != state
        assert drive.current_state.direction == entities.Direction.REVERSE
        assert drive.current_state.speed == entities.Speed(10)

        state = drive.current_state
        assert not drive.operate(
            direction=entities.Direction.REVERSE, speed=entities.Speed(10))
        assert drive.current_state == state
