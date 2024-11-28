from utils.hardware.WitMotion_dialog import WitMotionDialog
from utils.hardware.SingleMPU_Dialog import SingleMPUDialog
from utils.hardware.DoubleMPU_Dialog import DoubleMPUDialog
from utils.hardware.VideoCap import VideoCapture
from utils.hardware.CameraCap import CameraCapture
# from utils.hardware.deprecated.AravisCam import AravisCapture
from utils.hardware.DahengCam import DahengCapture

import threading


class HwDialog(object):
    """
                :NOTE:
                    Class which creates IMU and VideoCapture objects.
                    Supports all three implemented types.
                    Serves as a connector between main app and hardware implementations.
    """

    def __init__(self, QTOutput):
        self.HW_class = None
        self.videocap = None
        self.camera = None
        self.camera2 = None
        self.output = QTOutput
    
    def connectIMU(self, IMU_params_path, data_path):
        with open(IMU_params_path,'r') as f:
            lines = f.readlines()
        
        if lines[1].strip("\n") == '1':
        
            address = lines[3].strip('\n')
            baud_rate = int(lines[5].strip('\n'))
            self.connectedHW_type = lines[7].strip('\n')
            self.IMUmode = lines[9].strip('\n')
            self.savetype = lines[11].strip('\n')

            imu_types = {'WitMotion': WitMotionDialog, 'Single MPU': SingleMPUDialog, 'Double MPU': DoubleMPUDialog}
            if self.connectedHW_type in imu_types:
                self.HW_class = imu_types[self.connectedHW_type](QToutput=self.output, savepath=data_path)
            if self.HW_class is not None:
                self.HW_class.connect(port=address, baud_rate=baud_rate)
        
        else:
            self.connectedHW_type = None

    def connectVideoCap(self, data_path, vcap_params_path):
        with open(vcap_params_path,  'r') as file:
            lines = file.readlines()

        if lines[1].strip("\n") == '1':
            self.videocap = VideoCapture(QToutput=self.output, savepath=data_path,
                                         frameSize=lines[5].strip("\n").split('x'),
                                         fps=int(lines[7].strip("\n")))
            self.videocap.connect(cam_address=lines[3].strip("\n"))

    def connectCamera(self, data_path, camera_params_path):
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
                self.camera = CameraCapture(QToutput=self.output, savepath=data_path,
                                            frameSize=lines[7].strip("\n").split('x'),
                                            fps=int(lines[9].strip("\n")))
                self.camera.connect(cam_address=lines[5].strip("\n"))
            # elif lines[3].strip("\n") == 'Aravis':
            #     if lines[13].strip("\n") == '0':
            #         self.camera = AravisCapture(QToutput=self.output, savepath=data_path,
            #                                     frameSize=lines[7].strip("\n").split('x'),
            #                                     fps=int(lines[9].strip("\n")))
            #         self.camera.connect(cam_address=lines[5].strip("\n"))
            #     elif lines[13].strip("\n") == '1':
            #         self.camera = AravisCapture(QToutput=self.output, savepath=data_path,
            #                                     frameSize=lines[7].strip("\n").split('x'),
            #                                     fps=int(lines[9].strip("\n")))
            #         self.camera2 = AravisCapture(QToutput=self.output, savepath=data_path,
            #                                      frameSize=lines[7].strip("\n").split('x'),
            #                                      fps=int(lines[9].strip("\n")))
            #         self.camera.connect(cam_address='Daheng Imaging-2BA200004094-FCG23081373')
            #         self.camera2.connect(cam_address='Daheng Imaging-2BA200004095-FCG23081374')

            elif lines[3].strip("\n") == 'Daheng':
                if lines[13].strip("\n") == '0':
                    self.camera = DahengCapture(QToutput=self.output, savepath=data_path,
                                                frameSize=lines[7].strip("\n").split('x'),
                                                fps=int(lines[9].strip("\n")))
                    self.camera.connect(cam_address=lines[5].strip("\n"))
                elif lines[13].strip("\n") == '1':
                    self.camera = DahengCapture(QToutput=self.output, savepath=data_path,
                                                frameSize=lines[7].strip("\n").split('x'),
                                                fps=int(lines[9].strip("\n")))
                    self.camera2 = DahengCapture(QToutput=self.output, savepath=data_path,
                                                 frameSize=lines[7].strip("\n").split('x'),
                                                 fps=int(lines[9].strip("\n")))
                    self.camera.connect(cam_address='FCG23081373', cam_id='cam1')
                    self.camera2.connect(cam_address='FCG23081374', cam_id='cam2')
                    
            else:
                print('error')
            
    def MultipleConnect(self, IMU_params_path, data_path, vcap_params_path, camera_params_path):
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

        self.connectIMU(IMU_params_path=IMU_params_path, data_path=data_path)
        self.connectVideoCap(data_path=data_path, vcap_params_path=vcap_params_path)
        self.connectCamera(data_path=data_path, camera_params_path=camera_params_path)

    def disconnect_camera(self):
        if self.camera:
            self.camera.disconnect()
        
        if self.camera2:
            self.camera2.disconnect()

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
        
        if self.camera2:
            self.camera2.disconnect()
        
        self.output.append('Оборудование отключено')

    def _start_recording_thread(self, camera, cam_id):
        camera.start_recording(cam_id)

    def start_recording(self, start_recorder, start_camera):
        """
                    :NOTE:
                        Starts recording data using function of stated class.

                    :args:
                        mode (string): recording mode
                        start_recorder (bool): whether to start recorder or not; if not, use recorder in main app
        """

        if self.videocap:
            self.videocap.start_recording(start_recorder)

        if self.camera and start_camera:
            threading.Thread(target=self._start_recording_thread, args=(self.camera, 'cam1')).start()
        
        if self.camera2 and start_camera:
            threading.Thread(target=self._start_recording_thread, args=(self.camera2, 'cam2')).start()

        if self.connectedHW_type is not None:
            if self.connectedHW_type != 'WitMotion':
                self.HW_class.start_recording(self.IMUmode)
            else:
                self.HW_class.start_recording()
        
        self.output.append('Запись начата')
    
    def _stop_recording_thread(self, camera):
        camera.stop_recording()

    def stop_recording(self, stop_recorder, stop_camera):
        """
                    :NOTE:
                        Stops recording data and saves it using function of stated class.

                    :args:
                        savetype (string): name of data type to use when saving
                        stop_recorder (bool): whether to stop recorder or not; if not, use recorder in main app
        """

        if self.videocap:
            self.videocap.stop_recording(stop_recorder)

        if self.camera and stop_camera:
            threading.Thread(target=self._stop_recording_thread, args=(self.camera,)).start()
        
        if self.camera2 and stop_camera:
            threading.Thread(target=self._stop_recording_thread, args=(self.camera2,)).start()

        if self.connectedHW_type is not None:
            self.HW_class.stop_recording(self.savetype)
        
        self.output.append('Запись остановлена')
