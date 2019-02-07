import json
import os

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

from halalabs.iotrain import gateways, usecases, utils
from halalabs.iotrain.context import DriveContext
from halalabs.iotrain.controllers import DriveController
from halalabs.iotrain.entities import Drive


class IoTApp:
    def __init__(self,
                 thing_name: str,
                 endpoint_host: str,
                 endpoint_port: int,
                 root_ca_path: str,
                 private_key_path: str,
                 certificate_path: str,
                 connect_disconnect_timeout=10,
                 mqtt_operation_timeout=5):
        self.thing_name = thing_name
        self.client = AWSIoTMQTTShadowClient(thing_name)
        self.client.configureEndpoint(endpoint_host, endpoint_port)
        self.client.configureCredentials(root_ca_path, private_key_path,
                                         certificate_path)
        self.client.configureConnectDisconnectTimeout(
            connect_disconnect_timeout)
        self.client.configureMQTTOperationTimeout(mqtt_operation_timeout)

    def _delta_name(self):
        return 'delta/{thing_name}'.format(thing_name=self.thing_name)

    @utils.logging
    def _delta_callback(self, payload, response_status, token):
        if response_status == self._delta_name():
            payload_dict = json.loads(payload)
            if payload_dict['state'].get('drive'):
                self.controller.operate(payload_dict['state']['drive'])
        else:
            self.logger.error('responseStatus', response_status)

    @utils.logging
    def start(self):
        self.client.connect()
        self.shadow = self.client.createShadowHandlerWithName(
            self.thing_name, True)
        drive = Drive()
        drive_context = DriveContext(drive)
        motor_gateway = gateways.MotorGateway()
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
        self.client.disconnect()


def app():
    thing_name = os.environ['THING_NAME']
    endpoint_host = os.environ['ENDPOINT_HOST']
    root_ca_path = os.environ['ROOT_CA_PATH']
    private_key_path = os.environ['PRIVATE_KEY_PATH']
    certificate_path = os.environ['CERTIFICATE_PATH']

    iot_app = IoTApp(thing_name, endpoint_host, 8883, root_ca_path,
                     private_key_path, certificate_path)
    iot_app.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        iot_app.stop()
