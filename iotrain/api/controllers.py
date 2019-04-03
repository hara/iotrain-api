from iotrain.api import usecases, utils


class LocomotiveController:
    def __init__(self,
                 operate_input_port: usecases.ILocomotiveOperateInputPort):
        self.operate_input_port = operate_input_port

    @utils.logging
    def operate(self, operation: dict):
        input_data = usecases.LocomotiveOperateInputData.from_dict(operation)
        self.operate_input_port.execute(input_data)
