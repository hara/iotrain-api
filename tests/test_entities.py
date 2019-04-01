import pytest

from halalabs.iotrain.entities import Direction, Drive, Speed


class TestSpeed:
    @pytest.mark.parametrize("value", [0, 1, 99, 100])
    def test_valid_percentage(self, value):
        percentage = Speed(value)
        assert percentage.value == value

    @pytest.mark.parametrize("value", [-1, 101])
    def test_invalid_percentage(self, value):
        with pytest.raises(ValueError):
            Speed(value)

    def test_equality(self):
        assert Speed(0) == Speed(0)
        assert Speed(0) != Speed(1)
        assert Speed(0) != 0

    def test_str(self):
        assert str(Speed(0)) == '0'

    def test_repr(self):
        assert repr(Speed(0)) == '<Speed: 0>'


class TestDrive:
    def test_init(self):
        drive = Drive()
        assert drive.direction == Direction.STOP
        assert drive.speed == Speed(0)

    def test_operate(self):
        drive = Drive()
        drive.operate(Direction.BACKWARD, Speed(10))

        assert drive.direction == Direction.BACKWARD
        assert drive.speed == Speed(10)
