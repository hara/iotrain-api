from halalabs.iotrain.entities import Drive
from halalabs.iotrain.usecases import IDriveContext


class DriveContext(IDriveContext):
    def __init__(self, drive: Drive):
        self.drive = drive
