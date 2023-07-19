import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from App_GUI import Ui_MainWindow

from utils.IMU_dialog import IMUDialog


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
        self.WitMotionIMU = IMUDialog()
        self._connectSignalsAndSlots()

    def request_IMU_connect(self):
        self.WitMotionIMU.connect(port=self._view.IMU_port_lineEdit.text(), baud_rate=self._view.IMU_baud_rate_comboBox.currentText())

    def _connectSignalsAndSlots(self):
        self._view.IMU_connect_button.clicked.connect(lambda: self.request_IMU_connect())
        self._view.IMU_disconnect_button.clicked.connect(self.WitMotionIMU.disconnect)
        self._view.IMU_recording_start_button.clicked.connect(self.WitMotionIMU.start_recording)
        self._view.IMU_recording_stop_button.clicked.connect(self.WitMotionIMU.stop_recording)


class WitMotionConnectMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        sys.stdout = OutLog(self.output_textEdit, sys.stdout)


if __name__ == "__main__":
    WitMotionConnectApp = QApplication(sys.argv)
    WitMotionConnectWindow = WitMotionConnectMainWindow()
    WitMotionConnectWindow.show()
    WitMotionConnect(view=WitMotionConnectWindow)
    sys.exit(WitMotionConnectApp.exec())
