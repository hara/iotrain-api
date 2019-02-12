import json
import os

from AWSIoTPythonSDK.core.shadow.deviceShadow import deviceShadow
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

from halalabs.iotrain import gateways, motor, usecases, utils
from halalabs.iotrain.context import DriveContext
from halalabs.iotrain.controllers import DriveController
from halalabs.iotrain.entities import Drive


class App:
    def __init__(self, shadow: deviceShadow):
        self.shadow = shadow

    @utils.logging
    def _delta_callback(self, payload, response_status, token):
        payload_dict = json.loads(payload)
        if payload_dict['state'].get('drive'):
            self.controller.operate(payload_dict['state']['drive'])

    @utils.logging
    def start(self):
        drive = Drive()
        drive_context = DriveContext(drive)
        motor_gateway = gateways.MotorGateway(motor.motor())
        shadow_gateway = gateways.ShadowGateway(self.shadow)

        start_interactor = usecases.DriveStartInteractor(
            drive_context, shadow_gateway)

        operate_interactor = usecases.DriveOperateInteractor(
            drive_context, motor_gateway, shadow_gateway)

        self.controller = DriveController(start_interactor, operate_interactor)
        self.controller.start()
        self.shadow.shadowRegisterDeltaCallback(self._delta_callback)

    @utils.logging
    def stop(self):
        self.shadow.shadowUnregisterDeltaCallback()


def app():
    thing_name = os.environ['THING_NAME']
    endpoint_host = os.environ['ENDPOINT_HOST']
    root_ca_path = os.environ['ROOT_CA_PATH']
    private_key_path = os.environ['PRIVATE_KEY_PATH']
    certificate_path = os.environ['CERTIFICATE_PATH']

    client = AWSIoTMQTTShadowClient(thing_name)
    client.configureEndpoint(endpoint_host, 8883)
    client.configureCredentials(root_ca_path, private_key_path,
                                certificate_path)
    client.configureConnectDisconnectTimeout(10)
    client.configureMQTTOperationTimeout(5)

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
