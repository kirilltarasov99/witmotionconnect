import sys
import cv2
import numpy as np

from pathlib import Path

from utils.HwDialog import HwDialog
from utils.Decipher import Decipher
from utils.Mag_calibration import MagCal
from utils.Settings import Settings

from PySide6.QtWidgets import QWidget, QApplication, QLabel, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Slot, QThread, Signal, Qt
from PySide6.QtGui import QPixmap, QImage

loader = QUiLoader()


class WitMotionConnect(object):
    def __init__(self, view):
        self._view = view
        self.DecipherWindow = None
        self.MagCalWindow = None
        self.SettingsWindow = None
        self.USFeedWindow = None
        self.IMU = HwDialog()
        self._connectSignalsAndSlots()

        self.app_path = Path()
        self.settings_path = Path(self.app_path, 'settings/')
        self.magcal_params_path = Path(self.settings_path, 'magcal_params')
        self.vcap_params_path = Path(self.settings_path, 'vcap_params')
        self.data_path = Path(self.app_path, 'data/')

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
            lines = ['use\n', '1\n', 'address\n', '/dev/video2\n', 'res\n', '1920x1080\n', 'fps\n', '60\n',
                     'livefeed\n', '1280x720\n']
            with open(self.vcap_params_path, 'w') as file:
                file.writelines(lines)

    def request_IMU_connect(self):
        self.IMU.connect(QToutput=self._view.output_textEdit,
                         connectedHW_type=self._view.IMU_type_comboBox.currentText(),
                         port=self._view.IMU_port_lineEdit.text(),
                         baud_rate=self._view.IMU_baud_rate_comboBox.currentText(),
                         data_path=main_app.data_path,
                         vcap_params_path=self.vcap_params_path)

    def IMU_start_recording(self):
        self.IMU.start_recording(mode=self._view.IMU_mode_comboBox.currentText())

    def openDecipher(self):
        if self.DecipherWindow is None:
            decipher_ui_file = QFile('utils/GUI/DecipherWidget.ui')
            decipher_ui_file.open(QFile.ReadOnly)
            self.DecipherWindow = loader.load(decipher_ui_file)
            decipher_ui_file.close()
            DecipherAppClass(view=self.DecipherWindow)
            self.DecipherWindow.show()
            self.DecipherWindow = None

    def openMagCal(self):
        if self.MagCalWindow is None:
            magcal_ui_file = QFile('utils/GUI/magCalWidget.ui')
            magcal_ui_file.open(QFile.ReadOnly)
            self.MagCalWindow = loader.load(magcal_ui_file)
            magcal_ui_file.close()
            MagCalWidgetClass(view=self.MagCalWindow)
            self.MagCalWindow.show()
            self.MagCalWindow = None

    def openSettings(self):
        if self.SettingsWindow is None:
            settings_ui_file = QFile('utils/GUI/OptionsWidget.ui')
            settings_ui_file.open(QFile.ReadOnly)
            self.SettingsWindow = loader.load(settings_ui_file)
            settings_ui_file.close()
            SettingsWidgetClass(view=self.SettingsWindow)
            self.SettingsWindow.show()
            self.SettingsWindow = None

    def openUSFeed(self):
        if self.USFeedWindow is None:
            self.USFeedWindow = VideoFeed()
        self.USFeedWindow.show()

    def _connectSignalsAndSlots(self):
        self._view.IMU_connect_button.clicked.connect(lambda: self.request_IMU_connect())
        self._view.IMU_disconnect_button.clicked.connect(self.IMU.disconnect)
        self._view.IMU_recording_start_button.clicked.connect(lambda: self.IMU_start_recording())
        self._view.IMU_recording_stop_button.clicked.connect(self.IMU.stop_recording)
        self._view.decipher_action.triggered.connect(lambda: self.openDecipher())
        self._view.magCal_action.triggered.connect(lambda: self.openMagCal())
        self._view.settings_action.triggered.connect(lambda: self.openSettings())
        self._view.VideoFeed_pushButton.clicked.connect(lambda: self.openUSFeed())


class VideoThread(QThread):
    change_pixmap_signal = Signal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        cap = main_app.IMU.videocap.cap
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class VideoFeed(QWidget):
    def __init__(self):
        super().__init__()
        with open(main_app.vcap_params_path, 'r') as file:
            self.display_width, self.display_height = [eval(i) for i in file.readlines()[9].strip('\n').split('x')]
        self.setWindowTitle("УЗИ-сканирование")
        self.setFixedSize(self.display_width, self.display_height)
        self.image_label = QLabel(self)
        self.image_label.resize(self.display_width, self.display_height)

        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def closeEvent(self, event):
        self.thread.stop()
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


class MagCalWidgetClass(object):
    def __init__(self, view):
        self._view = view
        self.MagCal_obj = MagCal(QToutput=self._view.magCal_textEdit)
        self._connectSignalsAndSlots()

    def func_magCal(self):
        self.MagCal_obj.calibrate(MPU=main_app.IMU.HW_class, address=self._view.IMUaddress_comboBox.currentText(),
                                  params_path=main_app.magcal_params_path)

    def _connectSignalsAndSlots(self):
        self._view.magCal_pushButton.clicked.connect(lambda: self.func_magCal())


class SettingsWidgetClass(object):
    def __init__(self, view):
        self._view = view
        self.Settings_obj = Settings(main_app.vcap_params_path, self._view)
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
                                   params_path=main_app.magcal_params_path)

        self.Decipher_obj.save(file_name=self.fileName[0],
                               path=self.path,
                               table_format=self._view.saveformat_comboBox.currentText())

    def _connectSignalsAndSlots(self):
        self._view.openfile_pushButton.clicked.connect(lambda: self.showFileSelectDialog())
        self._view.decipher_pushButton.clicked.connect(lambda: self.func_decipher())


if __name__ == "__main__":
    WitMotionConnectApp = QApplication(sys.argv)
    main_ui_file = QFile('utils/GUI/app.ui')
    main_ui_file.open(QFile.ReadOnly)
    WitMotionConnectWindow = loader.load(main_ui_file)
    main_ui_file.close()
    main_app = WitMotionConnect(view=WitMotionConnectWindow)
    WitMotionConnectWindow.show()
    sys.exit(WitMotionConnectApp.exec())
