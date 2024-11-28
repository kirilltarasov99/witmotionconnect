import sys
import cv2
import numpy as np
import os
import time
import gxipy.gxiapi as gxiapi
import threading

from datetime import datetime
from pathlib import Path, PurePath
from utils.HwDialog import HwDialog
from utils.Decipher import Decipher
from utils.Mag_calibration import MagCal
from utils.Settings import Settings, CameraSettings, CameraSettings_updateValuesThread
# from utils.hardware.aravis import Camera as AravisCamera

from PySide6.QtWidgets import QWidget, QApplication, QLabel, QFileDialog, QMenuBar, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Slot, QThread, Signal, Qt
from PySide6.QtGui import QPixmap, QImage, QAction

loader = QUiLoader()

def loadUiWidget(ui_filename, parent=None):
    ui_file = QFile(ui_filename)
    ui_file.open(QFile.ReadOnly)
    ui = loader.load(ui_file)
    ui_file.close()
    
    return ui

class WitMotionConnect(object):
    def __init__(self, view):
        self._view = view
        self.DecipherWindow = None
        self.MagCalWindow = None
        self.SettingsWindow = None
        self.USFeedWindow = None
        self.CameraFeedWindow = None
        self.Camera2FeedWindow = None
        self.hardware = HwDialog(QTOutput=self._view.output_textEdit)
        self._connectSignalsAndSlots()

        self.app_path = Path()
        self.settings_path = Path(self.app_path, 'settings/')
        self.magcal_params_path = Path(self.settings_path, 'magcal_params')
        self.vcap_params_path = Path(self.settings_path, 'vcap_params')
        self.camera_params_path = Path(self.settings_path, 'camera_params')
        self.IMU_params_path = Path(self.settings_path, 'IMU_params')
        self.data_path = Path(self.app_path, 'data/')

        self.RecorderVideoWriter = None
        self.ext_recorder = False
        self.ins_recorder = False

        self.CameraVideoWriter = None
        self.ext_camera = False
        self.ins_camera = False
        self.rec_started = False
        self.rec_active = False

        self.create_default_params()


    def create_default_params(self):
        if not self.data_path.is_dir():
            self.data_path.mkdir()

        if not self.settings_path.is_dir():
            self.settings_path.mkdir()

        if not self.magcal_params_path.is_file():
            self._view.output_textEdit.append('Калибровочные параметры магнетометра не найдены, проведите калибровку!')
            lines = ['MPU1\n', '\n', '\n', 'MPU2\n', '\n', '\n']
            with open(self.magcal_params_path, 'w') as file:
                file.writelines(lines)

        if not self.vcap_params_path.is_file():
            self._view.output_textEdit.append('Создание дефолт параметров для рекордера')
            if os.name == 'nt':
                lines = ['use\n', '1\n', 'address\n', '0\n', 'res\n', '1920x1080\n', 'fps\n', '60\n',
                         'livefeed\n', '1280x720\n']
            else:
                lines = ['use\n', '0\n', 'address\n', '/dev/video2\n', 'res\n', '1920x1080\n', 'fps\n', '60\n',
                         'livefeed\n', '1280x720\n']
            with open(self.vcap_params_path, 'w') as file:
                file.writelines(lines)
        
        if not self.camera_params_path.is_file():
            self._view.output_textEdit.append('Создание дефолт параметров для камеры')
            if os.name == 'nt':
                lines = ['use\n', '1\n', 'type\n', 'Обычная\n', 'address\n', '0\n', 'res\n', '640x480\n', 'fps\n', '15\n',
                         'livefeed\n', '640x480\n']
            else:
                lines = ['use\n', '1\n', 'type\n', 'Обычная\n', 'address\n', '/dev/video0\n', 'res\n', '640x480\n', 'fps\n', '15\n',
                         'livefeed\n',  '640x480\n', 'second\n', '0\n']
            with open(self.camera_params_path,  'w') as file:
                file.writelines(lines)
        
        if not self.IMU_params_path.is_file():
            self._view.output_textEdit.append('Создание дефолт параметров для IMU')
            if os.name == 'nt':
                lines = ['use\n', '1\n', 'address\n', 'COM3\n', 'baudrate\n', '460800\n',
                         'type\n', 'Double MPU\n', 'mode\n', '6DoF\n', 'tabletype\n', '.npz\n']
            else:
                lines = ['use\n', '1\n', 'address\n', '/dev/ttyUSB0\n',  'baudrate\n', '460800\n',
                         'type\n',  'Double MPU\n',  'mode\n',  '6DoF\n',  'tabletype\n', '.npz\n']
            
            with open(self.IMU_params_path,  'w') as file:
                file.writelines(lines)

    def request_IMU_connect(self):
        if self.rec_active:
            QMessageBox.warning(self._view, "Warning", "Работает запись", QMessageBox.StandardButton.Ok)
            return
        self.hardware.MultipleConnect(IMU_params_path=self.IMU_params_path,
                                      data_path=main_app.data_path,
                                      vcap_params_path=self.vcap_params_path,
                                      camera_params_path=self.camera_params_path)
        
    def request_IMU_disconnect(self):
        if self.rec_active:
            QMessageBox.warning(self._view, "Warning", "Работает запись", QMessageBox.StandardButton.Ok)
            return
        
        self.hardware.disconnect()

    def IMU_start_recording(self):
        if self.rec_active:
            QMessageBox.warning(self._view, "Warning", "Запись уже запущена.", QMessageBox.StandardButton.Ok)
            return

        if self.USFeedWindow and self.CameraFeedWindow:
            self.RecorderVideoWriter = self.hardware.videocap.create_videowriter()
            self.ext_recorder = False
            self.CameraVideoWriter = self.hardware.camera.create_videowriter('cam1')
            self.ext_camera = False
            self.hardware.start_recording(start_recorder=self.ext_recorder, start_camera=self.ext_camera)
            self.ins_recorder = True
            self.ins_camera = True
            self.rec_started = True
        
        elif self.USFeedWindow:
            self.RecorderVideoWriter = self.hardware.videocap.create_videowriter()
            self.ext_recorder = False
            self.hardware.start_recording(start_recorder=self.ext_recorder, start_camera=self.ext_camera)
            self.ins_recorder = True
        
        elif self.CameraFeedWindow:
            self.CameraVideoWriter = self.hardware.camera.create_videowriter('cam1')
            self.ext_camera = False
            self.ext_recorder = True
            self.hardware.start_recording(start_recorder=self.ext_recorder, start_camera=self.ext_camera)
            self.ins_camera = True
            self.rec_started = True
        
        else:
            self.ext_camera = True
            self.ext_recorder = True
            self.hardware.start_recording(start_recorder=self.ext_recorder, start_camera=self.ext_camera)
        
        self.rec_active = True

    def IMU_stop_recording(self):
        if self.RecorderVideoWriter and self.CameraVideoWriter:
            self.ins_recorder = False
            self.ins_camera = False
            self.rec_started = False
            self.hardware.stop_recording(stop_recorder=self.ext_recorder, stop_camera=self.ext_camera)
            main_app.RecorderVideoWriter.release()
            main_app.RecorderVideoWriter = None
            self._view.output_textEdit.append('Рекордер остановлен')
            self._view.output_textEdit.append('Камера остановлена')
        
        elif self.RecorderVideoWriter:
            self.ins_recorder = False
            self.hardware.stop_recording(stop_recorder=self.ext_recorder, stop_camera=self.ext_camera)
            main_app.RecorderVideoWriter.release()
            main_app.RecorderVideoWriter = None
            self._view.output_textEdit.append('Рекордер остановлен')
        
        elif self.CameraVideoWriter:
            self.ins_camera = False
            self.rec_started = False
            self.hardware.stop_recording(stop_recorder=self.ext_recorder, stop_camera=self.ext_camera)
            self._view.output_textEdit.append('Камера остановлена')
        
        else:
            self.hardware.stop_recording(stop_recorder=self.ext_recorder, stop_camera=self.ext_camera)
        
        self.ext_recorder = False
        self.ext_camera = False
        self.rec_active = False

    def openDecipher(self):
        if self.DecipherWindow is None:
            self.DecipherWindow = loadUiWidget('utils/GUI/DecipherWidget.ui')
            DecipherAppClass(view=self.DecipherWindow)
            self.DecipherWindow.show()
            self.DecipherWindow = None

    def openMagCal(self):
        if self.MagCalWindow is None:
            self.MagCalWindow = loadUiWidget('utils/GUI/magCalWidget.ui')
            MagCalWidgetClass(view=self.MagCalWindow)
            self.MagCalWindow.show()
            self.MagCalWindow = None

    def openSettings(self):
        if self.SettingsWindow is None:
            self.SettingsWindow = loadUiWidget('utils/GUI/OptionsWidget.ui')
            SettingsWidgetClass(view=self.SettingsWindow)
            self.SettingsWindow.show()
            self.SettingsWindow = None

    def openUSFeed(self):
        if self.ext_recorder:
            QMessageBox.warning(self._view, "Warning", "Нельзя открыть трансляцию во время активной записи!", QMessageBox.StandardButton.Ok)
            return

        if self.USFeedWindow is None:
            self.USFeedWindow = USVideoFeed()
        self.USFeedWindow.show()
    
    def openCameraFeed(self, cam, feed):
        if self.ext_camera:
            QMessageBox.warning(self._view, "Warning", "Нельзя открыть трансляцию во время активной записи!", QMessageBox.StandardButton.Ok)
            return
        
        if feed == 1 and self.CameraFeedWindow is None:
            self.CameraFeedWindow = CameraVideoFeed(cam)
            self.CameraFeedWindow.show()

        elif feed == 2 and self.Camera2FeedWindow is None:
            self.Camera2FeedWindow = CameraVideoFeed(cam)
            self.Camera2FeedWindow.show()

    # debugging methods
    def debug_connectCamera(self):
        self.hardware.connectCamera(data_path=self.data_path, camera_params_path=self.camera_params_path)

    def _connectSignalsAndSlots(self):
        self._view.IMU_connect_button.clicked.connect(lambda: self.request_IMU_connect())
        self._view.IMU_disconnect_button.clicked.connect(lambda: self.request_IMU_disconnect())
        self._view.IMU_recording_start_button.clicked.connect(lambda: self.IMU_start_recording())
        self._view.IMU_recording_stop_button.clicked.connect(lambda: self.IMU_stop_recording())
        self._view.decipher_action.triggered.connect(lambda: self.openDecipher())
        self._view.magCal_action.triggered.connect(lambda: self.openMagCal())
        self._view.settings_action.triggered.connect(lambda: self.openSettings())
        self._view.USVideoFeed_button.clicked.connect(lambda: self.openUSFeed())
        self._view.CameraFeed_button.clicked.connect(lambda: self.openCameraFeed(self.hardware.camera, 1))
        self._view.Camera2Feed_button.clicked.connect(lambda: self.openCameraFeed(self.hardware.camera2, 2))
        # debug
        self._view.debug_cameraconnect_action.triggered.connect(lambda: self.debug_connectCamera())


class USVideoThread(QThread):       
    change_pixmap_signal = Signal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        cap = main_app.hardware.videocap.cap
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
                if main_app.ins_recorder:
                    main_app.RecorderVideoWriter.write(cv_img)

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class CameraThread(QThread):
    change_pixmap_signal = Signal(np.ndarray)
    record_frame_signal = Signal(datetime, np.ndarray)

    def __init__(self, camera):
        super().__init__()
        self._run_flag = True
        self.cap = camera
    
    def run(self):
        if isinstance(self.cap, cv2.VideoCapture):
            while self._run_flag:
                ret, cv_img = self.cap.read()
                if ret:
                    self.change_pixmap_signal.emit(cv_img)
                    if main_app.ins_camera:
                        main_app.CameraVideoWriter.write(cv_img)

        # elif isinstance(self.cap, AravisCamera):
        #     self.cap.start_acquisition_continuous()
        #     while self._run_flag:
        #         cv_img = cv2.cvtColor(self.cap.pop_frame(), cv2.COLOR_RGB2BGR)
        #         self.change_pixmap_signal.emit(cv_img)
        #         if main_app.ins_camera:
        #             main_app.CameraVideoWriter.write(cv_img)

        elif isinstance(self.cap, gxiapi.U3VDevice):
            self.cap.stream_on()
            while self._run_flag:
                raw_image = self.cap.data_stream[0].get_image()
                if raw_image is not None:
                    timestamp = datetime.now()
                    numpy_image = raw_image.get_numpy_array()
                    self.change_pixmap_signal.emit(numpy_image)
                    if main_app.ins_camera:
                        self.record_frame_signal.emit(timestamp, numpy_image)
                
                else:
                    print('Reconnecting')
                    main_app.hardware.disconnect_camera()
                    while True:
                        try:
                            self.cap = main_app.debug_connectCamera()
                        except gxiapi.OffLine:
                            time.sleep(0.5)
                        else:
                            self.cap = main_app.hardware.camera.cap
                            self.cap.stream_on()
                            break
            
        if main_app.ins_camera and not isinstance(self.cap, gxiapi.U3VDevice):
            main_app.CameraVideoWriter.release()
        
        if isinstance(self.cap, gxiapi.U3VDevice):
            self.cap.stream_off()
    
    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class USVideoFeed(QWidget):
    def __init__(self):
        super().__init__()
        with open(main_app.vcap_params_path, 'r') as file:
            self.display_width, self.display_height = [eval(i) for i in file.readlines()[9].strip('\n').split('x')]
        self.setWindowTitle("УЗИ-сканирование")
        self.setFixedSize(self.display_width, self.display_height)
        self.image_label = QLabel(self)
        self.image_label.resize(self.display_width, self.display_height)

        self.thread = USVideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def closeEvent(self, event):
        self.thread.stop()
        main_app.USFeedWindow = None
        event.accept()

    @Slot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.AspectRatioMode.KeepAspectRatio)
        return QPixmap.fromImage(p)
    

class CameraSettingsWidget(object):
    def __init__(self, view, camera):
        self._view = view
        self.camsettings_obj = CameraSettings(view, camera)
        self.thread = CameraSettings_updateValuesThread(camera=camera.cap)
        self.thread.new_expo_level.connect(self.camsettings_obj.updateExpoLevel)
        self.thread.new_framerate.connect(self.camsettings_obj.updateFPS)
        self.thread.start()
        self._connectSignalsAndSlots()

    def _connectSignalsAndSlots(self):
        self._view.expo_auto_pushButton.clicked.connect(lambda: self.camsettings_obj.set_expo_auto())
        self._view.set_expo_level_pushButton.clicked.connect(lambda: self.camsettings_obj.set_expo_manual())
        self._view.closeWidget_pushButton.clicked.connect(lambda: self.camsettings_obj.close_widget(self.thread))


class CameraVideoFeed(QWidget):
    def __init__(self, camera, parent=None):
        super().__init__(parent)
        with open(main_app.camera_params_path, 'r') as f:
            self.display_width, self.display_height  = [eval(i) for i in f.readlines()[11].strip('\n').split('x')]

        self.CameraSettingsWindow = None
        self.setWindowTitle("Камера для трекинга")
        self.setFixedSize(self.display_width, self.display_height)
        self.image_label = QLabel(self)
        self.image_label.resize(self.display_width, self.display_height)
        self.menu = QMenuBar(self)
        self.shot_action = QAction(text='Сделать снимок', parent=self.menu)
        self.camera_settings_action = QAction(text='Настроить экспозицию', parent=self.menu)
        self.menu.addAction(self.shot_action)
        self.menu.addAction(self.camera_settings_action)
        
        self._connectSignalsAndSlots()
        self.cv_img = None
        self.camera = camera

        self.thread = CameraThread(camera.cap)
        self.thread.change_pixmap_signal.connect(self.updateImage)
        self.thread.record_frame_signal.connect(self.write_frame)
        self.thread.start()

    def take_shot(self):
        if self.cv_img is not None:
            cv2.imwrite(str(PurePath(main_app.data_path, 'DCIM_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.jpg')), self.cv_img)
        
    def open_cam_settings(self):
        if self.CameraSettingsWindow is None:
                self.CameraSettingsWindow = loadUiWidget('utils/GUI/cam_settings.ui')
                CameraSettingsWidget(view=self.CameraSettingsWindow, camera=self.camera)
                self.CameraSettingsWindow.show()
                self.CameraSettingsWindow = None

    def closeEvent(self, event):
        self.thread.stop()
        main_app.CameraFeedWindow = None
        event.accept()
    
    def _connectSignalsAndSlots(self):
        self.shot_action.triggered.connect(lambda: self.take_shot())
        self.camera_settings_action.triggered.connect(lambda: self.open_cam_settings())

    @Slot(np.ndarray)
    def updateImage(self, cv_img):
        """Updates the image_label with a new opencv image"""
        self.cv_img = cv_img
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def write_frame(self, timestamp, frame):
        if main_app.ins_camera:
            if main_app.rec_started:
                self.start_time = datetime.now().strftime('%Y%m%d_%H%M%S')
                main_app.rec_started = False

            threading.Thread(target=self.camera.record_frame, args=(self.start_time, timestamp, frame, )).start()
    
    def convert_cv_qt(self, cv_img):
        h, w = cv_img.shape
        bytes_per_line = 1 * w
        convert_to_Qt_format = QImage(cv_img.data, w, h, bytes_per_line, QImage.Format.Format_Grayscale8)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.AspectRatioMode.KeepAspectRatio)
        return QPixmap.fromImage(p)


class MagCalWidgetClass(object):
    def __init__(self, view):
        self._view = view
        self.MagCal_obj = MagCal(QToutput=self._view.magCal_textEdit)
        self._connectSignalsAndSlots()

    def func_magCal(self):
        self.MagCal_obj.calibrate(MPU=main_app.hardware.HW_class, IMU_params_path=main_app.IMU_params_path,
                                  params_path=main_app.magcal_params_path)

    def _connectSignalsAndSlots(self):
        self._view.magCal_pushButton.clicked.connect(lambda: self.func_magCal())


class SettingsWidgetClass(object):
    def __init__(self, view):
        self._view = view
        self.Settings_obj = Settings(self._view, main_app.vcap_params_path, main_app.camera_params_path, main_app.IMU_params_path)
        self._connectSignalsAndSlots()

    def save_settings(self):
        self.Settings_obj.save()

    def _connectSignalsAndSlots(self):
        self._view.save_pushButton.clicked.connect(lambda: self.save_settings())


class DecipherAppClass(object):
    def __init__(self, view):
        self._view = view
        self.fileName = None
        self.Decipher_obj = Decipher(QToutput=self._view.info_textEdit)
        self._connectSignalsAndSlots()
        self.path = main_app.data_path

    def showFileSelectDialog(self):
        FileSelectDialog = QFileDialog()
        self.fileName = QFileDialog.getOpenFileName(FileSelectDialog, 'Выбор файла', str(self.path))
        if self.fileName[0] == '':
            self._view.info_textEdit.append('Файл не выбран')
        else:
            self._view.info_textEdit.append('Выбран файл ' + self.fileName[0])

    def func_decipher(self):
        self.Decipher_obj.open(file_name=self.fileName[0])
        self.Decipher_obj.decipher(acc_range=self._view.accelsense_comboBox.currentText(),
                                   gyro_range=self._view.gyrosense_comboBox.currentText(),
                                   params_path=main_app.magcal_params_path,
                                   calibration=self._view.calibrate_checkBox.isChecked())

        self.Decipher_obj.save(file_name=self.fileName[0],
                               path=self.path,
                               table_format=self._view.saveformat_comboBox.currentText())

    def _connectSignalsAndSlots(self):
        self._view.openfile_pushButton.clicked.connect(lambda: self.showFileSelectDialog())
        self._view.decipher_pushButton.clicked.connect(lambda: self.func_decipher())


if __name__ == "__main__":
    WitMotionConnectApp = QApplication(sys.argv)
    WitMotionConnectWindow = loadUiWidget('utils/GUI/app.ui')
    main_app = WitMotionConnect(view=WitMotionConnectWindow)
    WitMotionConnectWindow.show()
    sys.exit(WitMotionConnectApp.exec())
