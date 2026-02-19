import time
import gxipy.gxiapi as gxiapi
import cv2

from PySide6.QtCore import QThread, Signal


class Settings(object):
    """
                :NOTE:
                    Class for settings widget.

                :args:
                    params_path (pathlib.Path): path to videocap params
                    view (QWidget): QT Widget object which is used for Settings window
    """

    def __init__(self, view, recorder_params_path, camera_params_path, IMU_params_path):
        self.vcap_params_path = recorder_params_path
        self.camera_params_path = camera_params_path
        self.IMU_params_path = IMU_params_path
        self._view = view

        with open(self.vcap_params_path, 'r') as file:
            self.params_recorder = file.readlines()

        self._view.VCap_address_lineEdit.setText(self.params_recorder[3].strip('\n'))
        self._view.VCap_record_resolution_lineEdit.setText(self.params_recorder[5].strip('\n'))
        self._view.VCap_FPS_lineEdit.setText(self.params_recorder[7].strip('\n'))
        self._view.VCap_stream_resolution_lineEdit.setText(self.params_recorder[9].strip('\n'))

        with open(camera_params_path, 'r') as file:
            self.params_camera = file.readlines()
        
        self._view.Camera_type_comboBox.setCurrentText(self.params_camera[3].strip('\n'))
        self._view.Camera_address_lineEdit.setText(self.params_camera[5].strip('\n'))
        self._view.Camera_record_resolution_lineEdit.setText(self.params_camera[7].strip('\n'))
        self._view.Camera_FPS_lineEdit.setText(self.params_camera[9].strip('\n'))
        self._view.Camera_stream_resolution_lineEdit.setText(self.params_camera[11].strip('\n'))

        with open(IMU_params_path, 'r') as file:
            self.params_imu = file.readlines()
        
        self._view.IMU_address_lineEdit.setText(self.params_imu[3].strip('\n'))
        self._view.IMU_baud_rate_comboBox.setCurrentText(self.params_imu[5].strip('\n'))
        self._view.IMU_type_comboBox.setCurrentText(self.params_imu[7].strip('\n'))
        self._view.IMU_mode_comboBox.setCurrentText(self.params_imu[9].strip('\n'))
        self._view.table_type_comboBox.setCurrentText(self.params_imu[11].strip('\n'))
        
        if self.params_recorder[1].strip("\n") == '1':
            self.use_recorder = True
        else:
            self.use_recorder = False

        if self.params_camera[1].strip("\n") == '1':
            self.use_camera = True
        else:
            self.use_camera = False

        if self.params_camera[13].strip("\n") == '1':
            self.use_second_camera = True
        else:
            self.use_second_camera = False

        if self.params_imu[1].strip("\n") == '1':
            self.use_imu = True
        else:
            self.use_imu = False

        if self.use_recorder:
            self._view.VCap_use_checkBox.setChecked(1)

        if self.use_camera:
            self._view.Camera_use_checkBox.setChecked(1)
        
        if self.use_second_camera:
            self._view.Camera_second_use_checkBox.setChecked(1)
        
        if self.use_imu:
            self._view.IMU_use_checkBox.setChecked(1)
        
        self.currentIndexChanged()
        self._view.Camera_type_comboBox.currentIndexChanged.connect(self.currentIndexChanged)

    def currentIndexChanged(self):
        if self._view.Camera_type_comboBox.currentText() == "Aravis":
            self._view.Camera_second_use_checkBox.setEnabled(True)
            self._view.Camera_record_resolution_lineEdit.setEnabled(False)
            self._view.Camera_FPS_lineEdit.setEnabled(False)
            self._view.Camera_address_lineEdit.setText("Daheng Imaging-2BA200004094-FCG23081373")
        elif self._view.Camera_type_comboBox.currentText() == "Daheng":
            self._view.Camera_second_use_checkBox.setEnabled(True)
            self._view.Camera_record_resolution_lineEdit.setEnabled(False)
            self._view.Camera_FPS_lineEdit.setEnabled(False)
            # self._view.Camera_address_lineEdit.setText("FCG23081373")
        else:
            self._view.Camera_second_use_checkBox.setChecked(0)
            self._view.Camera_second_use_checkBox.setEnabled(False)
            self._view.Camera_record_resolution_lineEdit.setEnabled(True)
            self._view.Camera_FPS_lineEdit.setEnabled(True)
            self._view.Camera_address_lineEdit.setText("/dev/video2")

    def save(self):
        """
                :NOTE:
                    Saves settings into a text file.
        """

        if self._view.VCap_use_checkBox.isChecked():
            self.params_recorder[1] = '1\n'
        else:
            self.params_recorder[1] = '0\n'

        self.params_recorder[3] = str(self._view.VCap_address_lineEdit.text() + '\n')
        self.params_recorder[5] = str(self._view.VCap_record_resolution_lineEdit.text() + '\n')
        self.params_recorder[7] = str(self._view.VCap_FPS_lineEdit.text() + '\n')
        self.params_recorder[9] = str(self._view.VCap_stream_resolution_lineEdit.text() + '\n')

        with open(self.vcap_params_path, 'w') as file:
            file.writelines(self.params_recorder)

        if self._view.Camera_use_checkBox.isChecked():
            self.params_camera[1] = '1\n'
        else:
            self.params_camera[1] = '0\n'
        
        self.params_camera[3] = str(self._view.Camera_type_comboBox.currentText() + '\n')
        self.params_camera[5] = str(self._view.Camera_address_lineEdit.text() + '\n')
        self.params_camera[7] = str(self._view.Camera_record_resolution_lineEdit.text() + '\n')
        self.params_camera[9] = str(self._view.Camera_FPS_lineEdit.text() + '\n')
        self.params_camera[11] = str(self._view.Camera_stream_resolution_lineEdit.text() + '\n')
        
        if self._view.Camera_second_use_checkBox.isChecked():
            self.params_camera[13] = '1\n'
        else:
            self.params_camera[13] = '0\n'

        with open(self.camera_params_path, 'w') as file:
            file.writelines(self.params_camera)

        if self._view.IMU_use_checkBox.isChecked():
            self.params_imu[1] = '1\n'
        else:
            self.params_imu[1] = '0\n'
        
        self.params_imu[3] = str(self._view.IMU_address_lineEdit.text() + '\n')
        self.params_imu[5] = str(self._view.IMU_baud_rate_comboBox.currentText() + '\n')
        self.params_imu[7] = str(self._view.IMU_type_comboBox.currentText() + '\n')
        self.params_imu[9] = str(self._view.IMU_mode_comboBox.currentText() + '\n')
        self.params_imu[11] = str(self._view.table_type_comboBox.currentText() + '\n')

        with open(self.IMU_params_path, 'w') as file:
            file.writelines(self.params_imu)


class CameraSettings(object):
    def __init__(self, view, camera):
        self._view = view
        self.camera = camera
    
    def updateExpoLevel(self, expo_time):
        self._view.current_expo_level_label.setText(str(expo_time))

    def updateFPS(self, FPS_rate):
        self._view.FPS_label.setText(str(FPS_rate))

    def set_expo_auto(self):
        if isinstance(self.camera.cap, gxiapi.U3VDevice):
            self.camera.cap.ExposureAuto.set(2)
        elif isinstance(self.camera.cap, cv2.VideoCapture):
            auto_exp = self.camera.cap.get(cv2.CAP_PROP_AUTO_EXPOSURE)
            if auto_exp == 3.0:
                self.camera.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1.0)
            else:
                self.camera.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3.0)

    def set_expo_manual(self):
        try:
            value = int(self._view.set_expo_level_lineEdit.text())
            if isinstance(self.camera.cap, gxiapi.U3VDevice):
                self.camera.cap.ExposureTime.set(value)
            elif isinstance(self.camera.cap, cv2.VideoCapture):
                print("y")
                self.camera.cap.set(cv2.CAP_PROP_EXPOSURE, value)
        except ValueError:
            print("Значение не int")

    def close_widget(self, thread):
        thread.stop()
        self._view.close()


class CameraSettings_updateValuesThread(QThread):
    new_expo_level = Signal(int)
    new_framerate = Signal(float)

    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        self._run_flag = True

    def run(self):
        while self._run_flag:
            if isinstance(self.camera, gxiapi.U3VDevice):
                expo_level = self.camera.ExposureTime.get()
                self.new_expo_level.emit(expo_level)
                FPS_rate = self.camera.CurrentAcquisitionFrameRate.get()
                self.new_framerate.emit(FPS_rate)
                time.sleep(1)
            elif isinstance(self.camera, cv2.VideoCapture):
                auto_exp = self.camera.get(cv2.CAP_PROP_AUTO_EXPOSURE)
                if auto_exp == 3.0:
                    self.new_expo_level.emit(0)
                else:
                    expo_level = self.camera.get(cv2.CAP_PROP_EXPOSURE)
                    self.new_expo_level.emit(expo_level)
                FPS_rate = self.camera.get(cv2.CAP_PROP_FPS)
                self.new_framerate.emit(FPS_rate)
                time.sleep(1)
                
    
    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()
