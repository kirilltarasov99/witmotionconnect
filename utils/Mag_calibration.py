from time import sleep
from PyQt5 import QtTest


class MagCal:
    def __init__(self, QToutput):
        self.output = QToutput
        self.magBias = [0, 0, 0]

    def calibrate(self, MPU):
        MPU.reset_input_buffer()
        sleep(0.005)
        MPU.write((9).to_bytes(1, byteorder="big"))
        for i in range(4):
            info = str(MPU.readline())
            self.output.append(info)
        QtTest.QTest.qWait(30000)  # уточнить время работы
        for i in range(4):
            info = str(MPU.readline())
            self.output.append(info)
        MPU.reset_input_buffer()
