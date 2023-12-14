from utils.hardware.WitMotion_dialog import WitMotionDialog
from utils.hardware.SingleMPU_Dialog import SingleMPUDialog
from utils.hardware.DoubleMPU_Dialog import DoubleMPUDialog


class HwDialog(object):
    def __init__(self):
        self.HW_class = None

    def connect(self, QToutput, connectedHW_type, port, baud_rate, data_path):
        if connectedHW_type == 'WitMotion':
            self.HW_class = WitMotionDialog(QToutput=QToutput, savepath=data_path)
        elif connectedHW_type == 'Single MPU':
            self.HW_class = SingleMPUDialog(QToutput=QToutput, savepath=data_path)
        elif connectedHW_type == 'Double MPU':
            self.HW_class = DoubleMPUDialog(QToutput=QToutput, savepath=data_path)

        if self.HW_class is not None:
            self.HW_class.connect(port=port, baud_rate=baud_rate)

    def disconnect(self):
        self.HW_class.disconnect()

    def start_recording(self, mode):
        if self.HW_class is not WitMotionDialog:
            self.HW_class.start_recording(mode)
        else:
            self.HW_class.start_recording()

    def stop_recording(self):
        self.HW_class.stop_recording()
