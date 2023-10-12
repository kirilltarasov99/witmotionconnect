import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog
from App_GUI import Ui_WitMotionConnect_MainWindow
from Decipher_GUI import Ui_decipher_MainWindow

from utils.HW_Dialog import HW_Dialog
from utils.Decipher import Decipher


class OutLog:
    def __init__(self, edit, out=None, color=None):
        """(edit, out=None, color=None) -> can write stdout, stderr to a
        QTextEdit.
        edit = QTextEdit
        out = alternate stream ( can be the original sys.stdout )
        color = alternate color (i.e. color stderr a different color)
        """
        self.edit = edit
        self.out = None
        self.color = color

    def write(self, m):
        if self.color:
            tc = self.edit.textColor()
            self.edit.setTextColor(self.color)

        self.edit.moveCursor(QtGui.QTextCursor.End)
        self.edit.insertPlainText(m)

        if self.color:
            self.edit.setTextColor(tc)

        if self.out:
            self.out.write(m)


class WitMotionConnect:
    def __init__(self, view):
        self._view = view
        self.IMU = HW_Dialog()
        self._connectSignalsAndSlots()

    def request_IMU_connect(self):
        self.IMU.connect(connectedHW_type=self._view.IMU_type_comboBox.currentText(), port=self._view.IMU_port_lineEdit.text(),
                         baud_rate=self._view.IMU_baud_rate_comboBox.currentText())

    def openDecipher(self):
        DecipherAppWindow.show()
        DecipherAppClass(view=DecipherAppWindow)

    def _connectSignalsAndSlots(self):
        self._view.IMU_connect_button.clicked.connect(lambda: self.request_IMU_connect())
        self._view.IMU_disconnect_button.clicked.connect(self.IMU.disconnect)
        self._view.IMU_recording_start_button.clicked.connect(self.IMU.start_recording)
        self._view.IMU_recording_stop_button.clicked.connect(self.IMU.stop_recording)
        self._view.decipher_action.triggered.connect(lambda: self.openDecipher())


class DecipherAppClass:
    def __init__(self, view):
        self._view = view
        self.fileName = None
        self.Decipher_obj = Decipher()
        self._connectSignalsAndSlots()

    def showFileSelectDialog(self):
        FileSelectDialog = QFileDialog()
        self.fileName = QFileDialog.getOpenFileName(FileSelectDialog, 'Dialog Title', '/path/to/default/directory')

    def func_decipher(self):
        self.Decipher_obj.open(file_name=self.fileName)
        self.Decipher_obj.decipher()
        self.Decipher_obj.save(file_name=self.fileName, table_format='csv')

    def _connectSignalsAndSlots(self):
        self._view.openfile_pushButton.clicked.connect(lambda: self.showFileSelectDialog())
        self._view.decipher_pushButton.clicked.connect(lambda: self.func_decipher())


class WitMotionConnectMainWindow(QMainWindow, Ui_WitMotionConnect_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # sys.stdout = OutLog(self.output_textEdit, sys.stdout)


class WitMotionConnectDecipher(QMainWindow, Ui_decipher_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    WitMotionConnectApp = QApplication(sys.argv)
    WitMotionConnectWindow = WitMotionConnectMainWindow()
    DecipherApp = QApplication(sys.argv)
    DecipherAppWindow = WitMotionConnectDecipher()
    WitMotionConnectWindow.show()
    WitMotionConnect(view=WitMotionConnectWindow)

    DecipherAppWindow.close()
    sys.exit(WitMotionConnectApp.exec())
