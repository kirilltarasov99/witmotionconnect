import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QDialog
from GUI.App_GUI import Ui_WitMotionConnect_MainWindow
from GUI.Decipher_GUI import Ui_DecipherWidget
from GUI.MagCalibrationWidget import Ui_MagCalibrationWidget

from utils.HwDialog import HwDialog
from utils.Decipher import Decipher
from utils.Mag_calibration import MagCal


class WitMotionConnect:
    def __init__(self, view):
        self._view = view
        self.DecipherWindow = None
        self.MagCalWindow = None
        self.IMU = HwDialog()
        self._connectSignalsAndSlots()

    def request_IMU_connect(self):
        self.IMU.connect(output=self._view.output_textEdit,
                         connectedHW_type=self._view.IMU_type_comboBox.currentText(),
                         port=self._view.IMU_port_lineEdit.text(),
                         baud_rate=self._view.IMU_baud_rate_comboBox.currentText())

    def openDecipher(self):
        if self.DecipherWindow is None:
            self.DecipherWindow = DecipherAppWidget()
            DecipherAppClass(view=self.DecipherWindow)
            self.DecipherWindow.show()
            self.DecipherWindow.exec_()
            self.DecipherWindow = None

    def openMagCal(self):
        if self.MagCalWindow is None:
            self.MagCalWindow = MagCalibrationAppWidget()
            MagCalWidgetClass(view=self.MagCalWindow)
            self.MagCalWindow.show()
            self.MagCalWindow.exec_()
            self.MagCalWindow = None

    def _connectSignalsAndSlots(self):
        self._view.IMU_connect_button.clicked.connect(lambda: self.request_IMU_connect())
        self._view.IMU_disconnect_button.clicked.connect(self.IMU.disconnect)
        self._view.IMU_recording_start_button.clicked.connect(self.IMU.start_recording)
        self._view.IMU_recording_stop_button.clicked.connect(self.IMU.stop_recording)
        self._view.decipher_action.triggered.connect(lambda: self.openDecipher())
        self._view.magCal_action.triggered.connect(lambda: self.openMagCal())


class MagCalWidgetClass:
    def __init__(self, view):
        self._view = view
        self.MagCal_obj = MagCal(output=self._view.magCal_textEdit)
        self._connectSignalsAndSlots()

    def func_magCal(self):
        self.MagCal_obj.calibrate(MPU=main_app.IMU.HW_class.MPUInterface)

    def _connectSignalsAndSlots(self):
        self._view.magCal_pushButton.clicked.connect(lambda: self.func_magCal())


class DecipherAppClass:
    def __init__(self, view):
        self._view = view
        self.fileName = None
        self.Decipher_obj = Decipher(output=self._view.info_textEdit)
        self._connectSignalsAndSlots()

    def showFileSelectDialog(self):
        FileSelectDialog = QFileDialog()
        self.fileName = QFileDialog.getOpenFileName(FileSelectDialog, 'Dialog Title', '/path/to/default/directory')
        if self.fileName[0] == '':
            self._view.info_textEdit.append('Файл не выбран')
        else:
            self._view.info_textEdit.append('Выбран файл ' + self.fileName[0])

    def func_decipher(self):
        self.Decipher_obj.open(file_name=self.fileName)
        self.Decipher_obj.decipher(acc_range=self._view.accelsense_comboBox.currentText(),
                                   gyro_range=self._view.gyrosense_comboBox.currentText())

        self.Decipher_obj.save(file_name=self.fileName, table_format=self._view.saveformat_comboBox.currentText())

    def _connectSignalsAndSlots(self):
        self._view.openfile_pushButton.clicked.connect(lambda: self.showFileSelectDialog())
        self._view.decipher_pushButton.clicked.connect(lambda: self.func_decipher())


class WitMotionConnectMainWindow(QMainWindow, Ui_WitMotionConnect_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class DecipherAppWidget(QDialog, Ui_DecipherWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class MagCalibrationAppWidget(QDialog, Ui_MagCalibrationWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    WitMotionConnectApp = QApplication(sys.argv)
    WitMotionConnectWindow = WitMotionConnectMainWindow()
    main_app = WitMotionConnect(view=WitMotionConnectWindow)
    WitMotionConnectWindow.show()
    sys.exit(WitMotionConnectApp.exec())
