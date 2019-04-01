from halalabs.iotrain import usecases, utils


class DriveController:
    def __init__(self, operate_input_port: usecases.IDriveOperateInputPort):
        self.operate_input_port = operate_input_port

    @utils.logging
    def operate(self, operation: dict):
        input_data = usecases.DriveOperateInputData.from_dict(operation)
        self.operate_input_port.execute(input_data)
