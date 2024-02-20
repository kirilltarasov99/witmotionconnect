import sys

from pathlib import Path

from utils.HwDialog import HwDialog
from utils.Decipher import Decipher
from utils.Mag_calibration import MagCal

from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

loader = QUiLoader()


class WitMotionConnect(object):
    def __init__(self, view):
        self._view = view
        self.DecipherWindow = None
        self.MagCalWindow = None
        self.IMU = HwDialog()
        self._connectSignalsAndSlots()
        self.params_path = Path('./magcal_params')
        self.vcap_params_path = Path('./vcap_params')
        self.data_path = Path('./data/')

        if not self.data_path.is_dir():
            self.data_path.mkdir()

        if not self.params_path.is_file():
            self._view.output_textEdit.append('Калибровочные параметры магнетометра не найдены, проведите калибровку!')
            lines = ['MPU1\n', '\n', '\n', 'MPU2\n', '\n', '\n']
            with open(self.params_path, 'w') as file:
                file.writelines(lines)

        if not self.vcap_params_path.is_file():
            self._view.output_textEdit.append('Создание дефолт параметров для рекордера')
            lines = ['use\n', '1\n', 'address\n', '/dev/video2\n', 'res\n', '1920\t1080\n', 'fps\n', '60\n']
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

    def _connectSignalsAndSlots(self):
        self._view.IMU_connect_button.clicked.connect(lambda: self.request_IMU_connect())
        self._view.IMU_disconnect_button.clicked.connect(self.IMU.disconnect)
        self._view.IMU_recording_start_button.clicked.connect(lambda: self.IMU_start_recording())
        self._view.IMU_recording_stop_button.clicked.connect(self.IMU.stop_recording)
        self._view.decipher_action.triggered.connect(lambda: self.openDecipher())
        self._view.magCal_action.triggered.connect(lambda: self.openMagCal())


class MagCalWidgetClass(object):
    def __init__(self, view):
        self._view = view
        self.MagCal_obj = MagCal(QToutput=self._view.magCal_textEdit)
        self._connectSignalsAndSlots()

    def func_magCal(self):
        self.MagCal_obj.calibrate(MPU=main_app.IMU.HW_class, address=self._view.IMUaddress_comboBox.currentText(),
                                  params_path=main_app.params_path)

    def _connectSignalsAndSlots(self):
        self._view.magCal_pushButton.clicked.connect(lambda: self.func_magCal())


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
                                   params_path=main_app.params_path)

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
