import json

from AWSIoTPythonSDK.core.shadow.deviceShadow import deviceShadow
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from click import argument, command, option

from halalabs.iotrain import gateways, motor, usecases, utils
from halalabs.iotrain.controllers import LocomotiveController
from halalabs.iotrain.entities import Locomotive


class App:
    def __init__(self, shadow: deviceShadow):
        self.shadow = shadow
        locomotive = Locomotive()
        motor_gateway = gateways.MotorGateway(motor.motor())
        shadow_gateway = gateways.ShadowGateway(self.shadow)
        operate_interactor = usecases.LocomotiveOperateInteractor(
            locomotive, motor_gateway, shadow_gateway)
        self.controller = LocomotiveController(operate_interactor)

    @utils.logging
    def _delta_callback(self, payload, response_status, token):
        payload_dict = json.loads(payload)
        if payload_dict['state'].get('drive'):
            self.controller.operate(payload_dict['state']['drive'])

    @utils.logging
    def start(self):
        self.shadow.shadowRegisterDeltaCallback(self._delta_callback)

    @utils.logging
    def stop(self):
        self.shadow.shadowUnregisterDeltaCallback()


@command()
@argument('thing-name')
@option('-e', '--endpoint', help='AWS IoT Core endpoint.', metavar='HOSTNAME')
@option(
    '-r',
    '--root-ca',
    default='./certs/AmazonRootCA1.pem',
    help='Root CA file.',
    metavar='PATH')
@option(
    '-p',
    '--private-key',
    default='./certs/private.pem.key',
    help='Private key file.',
    metavar='PATH')
@option(
    '-c',
    '--certificate',
    default='./certs/certificate.pem.crt',
    help='Certificate file.',
    metavar='PATH')
def cli(thing_name, endpoint, root_ca, private_key, certificate):
    """iotrain - An IoT Train app."""
    client = AWSIoTMQTTShadowClient(thing_name)
    client.configureEndpoint(endpoint, 8883)
    client.configureCredentials(root_ca, private_key, certificate)
    client.configureConnectDisconnectTimeout(10)
    client.configureMQTTOperationTimeout(10)

    client.connect()
    try:
        shadow = client.createShadowHandlerWithName(thing_name, True)
        app = App(shadow)
        app.start()
        while True:
            pass
    except KeyboardInterrupt:
        app.stop()
        client.disconnect()
