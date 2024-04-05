import serial
import pandas as pd

from pathlib import PurePath
from datetime import datetime
from threading import Thread, Event
from time import sleep


class SingleMPUDialog(object):
    """
                :NOTE:
                    Class to use with Single MPU connection mode and Arduino FW.

                :args:
                    QToutput (QTextEdit): GUI object for output messages
                    savepath (pathlib.Path): path to data folder
    """

    def __init__(self, QToutput, savepath):
        self.output = QToutput
        self.savepath = savepath
        self.mode = None
        self.MPUInterface = None
        self.datetime_list = []
        self.MPUdata = []
        self.pause_event = Event()
        self.recorder_thread = None

    def connect(self, port, baud_rate):
        """
                    :NOTE:
                        Opens serial connection to IMU.

                    :args:
                        port (string): serial port address
                        baud_rate (string): baud rate value
        """

        self.MPUInterface = serial.Serial(port=port, baudrate=baud_rate)
        self.output.append('Датчик подключен')

    def disconnect(self):
        """
                    :NOTE:
                        Closes serial connection to IMU.
        """

        self.MPUInterface.close()
        self.output.append('Датчик отключен')

    def recorder(self):
        """
                    :NOTE:
                        Records incoming data from IMU into list buffer.
        """

        self.MPUInterface.reset_input_buffer()
        sleep(0.005)
        while self.MPUInterface.is_open is True:
            if self.pause_event.is_set():
                self.MPUInterface.reset_input_buffer()
                break

            match self.mode:
                case '6DoF':
                    sleep(0.00045)
                    self.datetime_list.append(datetime.now())
                    self.MPUdata.append(self.MPUInterface.read(12))
                case '9DoF':
                    sleep(0.00045)
                    self.datetime_list.append(datetime.now())
                    self.MPUdata.append(self.MPUInterface.read(18))

    def start_recording(self, mode):
        """
                    :NOTE:
                        Starts recording data.

                    :args:
                        mode (string): recording mode
        """

        self.mode = mode
        self.MPUdata = []
        self.datetime_list = []
        self.pause_event.clear()
        match self.mode:
            case '6DoF':
                self.output.append('Начата запись... режим 6DoF 1000 Hz')
                self.MPUInterface.write((2).to_bytes(1, byteorder='big'))
            case '9DoF':
                self.output.append('Начата запись... режим 9DoF ~900 Hz')
                self.MPUInterface.write((4).to_bytes(1, byteorder='big'))
        self.recorder_thread = Thread(target=self.recorder)
        self.recorder_thread.start()

    def stop_recording(self):
        """
                    :NOTE:
                        Stops recording data and saves it to hdf table.
        """

        self.MPUInterface.write((1).to_bytes(1, byteorder='big'))
        self.pause_event.set()
        self.recorder_thread.join()
        self.output.append('Запись остановлена')
        match savetype:
            case '.h5':
                DF_savename = PurePath(self.savepath, 'Single_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.h5')
                Data_df = pd.DataFrame({'SystemTime': self.datetime_list,
                                        'MPU1_data': self.MPU1_data})
                Data_df.to_hdf(DF_savename, key='data', index=False)

            case '.csv':
                DF_savename = PurePath(self.savepath, 'Single_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv')
                Data_df = pd.DataFrame({'SystemTime': self.datetime_list,
                                        'MPU1_data': self.MPU1_data})
                Data_df.to_csv(DF_savename, index=False)

            case '.npz':
                DF_savename = PurePath(self.savepath, 'Single_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.npz')
                np.savez(DF_savename, SystemTime=self.datetime_list, MPU1_data=self.MPU1_data)

        self.output.append('Данные сохранены')
