from utils.hardware.WitMotion_dialog import WitMotionDialog
from utils.hardware.SingleMPU_Dialog import SingleMPUDialog
from utils.hardware.DoubleMPU_Dialog import DoubleMPUDialog
from utils.hardware.VideoCap import VideoCapture
from utils.hardware.CameraCap import CameraCapture
from utils.hardware.AravisCam import AravisCapture


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
        self.camera = None
    
    def connectIMU(self, QToutput, IMU_params_path, data_path):
        with open(IMU_params_path,'r') as f:
            lines = f.readlines()
        
        address = lines[3].strip('\n')
        baud_rate = int(lines[5].strip('\n'))
        self.connectedHW_type = lines[7].strip('\n')
        self.IMUmode = lines[9].strip('\n')
        self.savetype = lines[11].strip('\n')

        imu_types = {'WitMotion': WitMotionDialog, 'Single MPU': SingleMPUDialog, 'Double MPU': DoubleMPUDialog}
        if self.connectedHW_type in imu_types:
            self.HW_class = imu_types[self.connectedHW_type](QToutput=QToutput, savepath=data_path)
        if self.HW_class is not None:
            self.HW_class.connect(port=address, baud_rate=baud_rate)

    def connectVideoCap(self, QToutput, data_path, vcap_params_path):
        with open(vcap_params_path,  'r') as file:
            lines = file.readlines()

        if lines[1].strip("\n") == '1':
            self.videocap = VideoCapture(QToutput=QToutput, savepath=data_path,
                                         frameSize=lines[5].strip("\n").split('x'),
                                         fps=int(lines[7].strip("\n")))
            self.videocap.connect(cam_address=lines[3].strip("\n"))

    def connectCamera(self, QToutput, data_path, camera_params_path):
        """
                    :NOTE:
                        Connect to a camera based on the parameters specified in a configuration file.

                    :args:
                        QToutput (method): Function for outputting messages from this class's methods to be used by the calling application.
                        data_path (str): Path where recorded data will be stored.
                        camera_params_path (str): File path of configuration file specifying connection parameters, including frame size and fps.
        """
        
        with open(camera_params_path,  'r') as file:
            lines = file.readlines()
        
        if lines[1].strip("\n") == '1':
            if lines[3].strip("\n") == 'Обычная':
                self.camera = CameraCapture(QToutput=QToutput, savepath=data_path,
                                        frameSize=lines[5].strip("\n").split('x'),
                                        fps=int(lines[7].strip("\n")))
                self.camera.connect(cam_address=lines[3].strip("\n"))
            elif lines[3].strip("\n") == 'Aravis':
                self.camera = AravisCapture(QToutput=QToutput, savepath=data_path,
                                            frameSize=lines[7].strip("\n").split('x'),
                                            fps=int(lines[9].strip("\n")))
                self.camera.connect(cam_address=lines[5].strip("\n"))
            else:
                print('error')
            
    def MultipleConnect(self, QToutput, IMU_params_path, data_path, vcap_params_path, camera_params_path):
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

        self.connectIMU(QToutput=QToutput, IMU_params_path=IMU_params_path, data_path=data_path)
        self.connectVideoCap(QToutput=QToutput, data_path=data_path, vcap_params_path=vcap_params_path)
        self.connectCamera(QToutput=QToutput, data_path=data_path, camera_params_path=camera_params_path)

    def disconnect(self):
        """
                    :NOTE:
                        Closes serial connection to IMU using function of stated class, and releases the capture card.
        """

        if self.HW_class:
            self.HW_class.disconnect()
        
        if self.videocap:
            self.videocap.disconnect()
        
        if self.camera:
            self.camera.disconnect()

    def start_recording(self, start_recorder, start_camera):
        """
                    :NOTE:
                        Starts recording data using function of stated class.

                    :args:
                        mode (string): recording mode
                        start_recorder (bool): whether to start recorder or not; if not, use recorder in main app
        """

        if self.videocap and start_recorder:
            self.videocap.start_recording()

        if self.camera and start_camera:
            self.camera.start_recording()

        if self.connectedHW_type != 'WitMotion':
            self.HW_class.start_recording(self.IMUmode)
        else:
            self.HW_class.start_recording()

    def stop_recording(self, stop_recorder, stop_camera):
        """
                    :NOTE:
                        Stops recording data and saves it using function of stated class.

                    :args:
                        savetype (string): name of data type to use when saving
                        stop_recorder (bool): whether to stop recorder or not; if not, use recorder in main app
        """

        if self.videocap and stop_recorder:
            self.videocap.stop_recording()

        if self.camera and stop_camera:
            self.camera.stop_recording()

        self.HW_class.stop_recording(self.savetype)
