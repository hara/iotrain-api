from halalabs.iotrain import usecases, utils


class DriveController:
    def __init__(self, start_input_port: usecases.IDriveStartInputPort,
                 operate_input_port: usecases.IDriveOperateInputPort):
        self.start_input_port = start_input_port
        self.operate_input_port = operate_input_port

    @utils.logging
    def start(self):
        self.start_input_port.execute()

    @utils.logging
    def operate(self, operation: dict):
        input_data = usecases.DriveOperateInputData.from_dict(operation)
        self.operate_input_port.execute(input_data)
