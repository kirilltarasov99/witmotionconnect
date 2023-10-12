from utils.hardware.WitMotion_dialog import WitMotionDialog
from utils.hardware.SingleMPU_Dialog import SingleMPUDialog
from utils.hardware.DoubleMPU_Dialog import DoubleMPUDialog


class HW_Dialog:
    def __init__(self):
        self.HW_class = None

    def connect(self, connectedHW_type, port, baud_rate):
        if connectedHW_type == 'WitMotion':
            self.HW_class = WitMotionDialog()
        elif connectedHW_type == 'Single MPU':
            self.HW_class = SingleMPUDialog()
        elif connectedHW_type == 'Double MPU':
            self.HW_class = DoubleMPUDialog()

        if self.HW_class is not None:
            self.HW_class.connect(port=port, baud_rate=baud_rate)

    def disconnect(self):
        self.HW_class.disconnect()

    def start_recording(self):
        self.HW_class.start_recording()

    def stop_recording(self):
        self.HW_class.stop_recording()
