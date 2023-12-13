from time import sleep
from PyQt5 import QtTest


class MagCal:
    def __init__(self, QToutput):
        self.output = QToutput

    def calibrate(self, MPU, address, params_path):
        interface = MPU.MPUInterface
        interface.reset_input_buffer()
        sleep(0.005)
        MPU_type = str(type(MPU))
        if MPU_type == "<class 'utils.hardware.SingleMPU_Dialog.SingleMPUDialog'>":
            interface.write((9).to_bytes(1, byteorder="big"))
        elif MPU_type == "<class 'utils.hardware.DoubleMPU_Dialog.DoubleMPUDialog'>":
            if address == 'I2C1, 0x68':
                interface.write((9).to_bytes(1, byteorder="big"))
            elif address == 'I2C1, 0x69':
                interface.write((8).to_bytes(1, byteorder="big"))

        with open(params_path, 'r') as file:
            lines = file.readlines()

        for i in range(4):
            info = str(interface.readline())
            self.output.append(info)
        QtTest.QTest.qWait(30000)  # уточнить время работы
        for i in range(4):
            info = str(interface.readline())
            self.output.append(info)
            if i == 1 or i == 2:
                if (MPU_type == "<class 'utils.hardware.SingleMPU_Dialog.SingleMPUDialog'>") or (MPU_type == "<class 'utils.hardware.DoubleMPU_Dialog.DoubleMPUDialog'>" and address == 'I2C1, 0x68'):
                    lines[i] = info[2:-5] + '\n'
                elif (MPU_type == "<class 'utils.hardware.DoubleMPU_Dialog.DoubleMPUDialog'>" and address == 'I2C1, 0x69'):
                    lines[i+3] = info[2:-5] + '\n'

        with open(params_path, 'w') as file:
            file.writelines(lines)
        interface.reset_input_buffer()
