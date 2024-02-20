from utils.hardware.WitMotion_dialog import WitMotionDialog
from utils.hardware.SingleMPU_Dialog import SingleMPUDialog
from utils.hardware.DoubleMPU_Dialog import DoubleMPUDialog
from utils.hardware.VideoCap import VideoCapture


class HwDialog(object):
    """
                :NOTE:
                    Class which creates IMU and VideoCapture objects.
                    Supports all three implemented types.
                    Serves as a connector between main app and hardware implementations.
    """

    def __init__(self):
        self.HW_class = None
        self.videocap = None

    def connect(self, QToutput, connectedHW_type, port, baud_rate, data_path, vcap_params_path):
        """
                    :NOTE:
                        Creates IMU and VideoCapture objects and connects the IMU.

                    :args:
                        QToutput (QTextEdit): GUI object for output messages
                        connectedHW_type (string): IMU type to use
                        port (string): serial port address
                        baud_rate (string): baud rate
                        data_path (pathlib.Path): path to data folder
                        vcap_params_path (pathlib.Path): path to videocap params
        """
        with open(vcap_params_path, 'r') as file:
            lines = file.readlines()

        if lines[1].strip("\n") == '1':
            self.videocap = VideoCapture(QToutput=QToutput, savepath=data_path,
                                         frameSize=lines[5].strip("\n").split('x'),
                                         fps=int(lines[7].strip("\n")))
            self.videocap.connect(cam_address=lines[3].strip("\n"))

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
                        Closes serial connection to IMU using function of stated class, and releases the capture card.
        """

        self.HW_class.disconnect()
        if self.videocap:
            self.videocap.disconnect()

    def start_recording(self, mode):
        """
                    :NOTE:
                        Starts recording data using function of stated class.

                    :args:
                        mode (string): recording mode
        """
        if self.videocap:
            self.videocap.start_recording()

        if self.HW_class is not WitMotionDialog:
            self.HW_class.start_recording(mode)
        else:
            self.HW_class.start_recording()

    def stop_recording(self):
        """
                    :NOTE:
                        Stops recording data and saves it using function of stated class.
        """

        if self.videocap:
            self.videocap.stop_recording()

        self.HW_class.stop_recording()
