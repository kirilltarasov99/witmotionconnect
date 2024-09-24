from time import sleep
from PySide6 import QtTest


class MagCal(object):
    """
                :NOTE:
                    Class for magnetometer calibration function of the app.

                :args:
                    QToutput (QTextEdit): GUI object for output messages
    """

    def __init__(self, QToutput):
        self.output = QToutput

    def calibrate(self, MPU, IMU_params_path, params_path):
        """
                    :NOTE:
                        Performs magnetometer calibration on supported IMUs.

                    :args:
                        MPU (): IMU to use
                        address (string): I2C address of MPU on microcontroller.
                        params_path (pathlib.Path): path of magnetometer calibration parameters.
        """

        interface = MPU.MPUInterface
        interface.reset_input_buffer()
        with open(IMU_params_path,'r') as f:
            lines = f.readlines()
        
        address = lines[3].strip('\n')
        sleep(0.005)
        MPU_type = str(type(MPU))
        if MPU_type == "<class 'utils.hardware.SingleMPU_Dialog.SingleMPUDialog'>":
            interface.write((9).to_bytes(1, byteorder='big'))
        elif MPU_type == "<class 'utils.hardware.DoubleMPU_Dialog.DoubleMPUDialog'>":
            if address == 'I2C1, 0x68':
                interface.write((9).to_bytes(1, byteorder='big'))
            elif address == 'I2C1, 0x69':
                interface.write((8).to_bytes(1, byteorder='big'))

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
