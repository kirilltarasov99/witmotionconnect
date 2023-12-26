from utils.hardware.WitMotion_dialog import WitMotionDialog
from utils.hardware.SingleMPU_Dialog import SingleMPUDialog
from utils.hardware.DoubleMPU_Dialog import DoubleMPUDialog


class HwDialog(object):
    """
                :NOTE:
                    Class which creates an IMU object.
                    Supports all three implemented types.
                    Serves as a connector between main app and hardware implementations.
    """

    def __init__(self):
        self.HW_class = None

    def connect(self, QToutput, connectedHW_type, port, baud_rate, data_path):
        """
                    :NOTE:
                        Creates an IMU object and connects the IMU.

                    :args:
                        QToutput (QTextEdit): GUI object for output messages
                        connectedHW_type (string): IMU type to use
                        port (string): serial port address
                        baud_rate (string): baud rate
                        data_path (pathlib.Path): path to data folder
        """

        if connectedHW_type == 'WitMotion':
            self.HW_class = WitMotionDialog(QToutput=QToutput, savepath=data_path)
        elif connectedHW_type == 'Single MPU':
            self.HW_class = SingleMPUDialog(QToutput=QToutput, savepath=data_path)
        elif connectedHW_type == 'Double MPU':
            self.HW_class = DoubleMPUDialog(QToutput=QToutput, savepath=data_path)

        if self.HW_class is not None:
            self.HW_class.connect(port=port, baud_rate=baud_rate)

    def disconnect(self):
        """
                    :NOTE:
                        Closes serial connection to IMU using function of stated class.
        """

        self.HW_class.disconnect()

    def start_recording(self, mode):
        """
                    :NOTE:
                        Starts recording data using function of stated class.

                    :args:
                        mode (string): recording mode
        """

        if self.HW_class is not WitMotionDialog:
            self.HW_class.start_recording(mode)
        else:
            self.HW_class.start_recording()

    def stop_recording(self):
        """
                    :NOTE:
                        Stops recording data and saves it using function of stated class.
        """

        self.HW_class.stop_recording()
