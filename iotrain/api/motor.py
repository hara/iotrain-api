from iotrain.api import utils

explorerhat = None
try:
    from smbus import SMBus
    import explorerhat
except ImportError:
    pass


class DummyMotor:
    def speed(self, value: int):
        utils.logger.info("speed={value}".format(value=value))


@utils.logging
def motor():
    if explorerhat:
        return explorerhat.motor.one
    else:
        return DummyMotor()
