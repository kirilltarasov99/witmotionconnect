import serial
import pandas as pd
import os

from datetime import datetime
from threading import Thread, Event
from time import sleep


class SingleMPUDialog:
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
        self.MPUInterface = serial.Serial(port=port, baudrate=baud_rate)
        self.output.append("Датчик подключен")

    def disconnect(self):
        self.MPUInterface.close()
        self.output.append("Датчик отключен")

    def recorder(self):
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
        self.mode = mode
        self.MPUdata = []
        self.datetime_list = []
        self.pause_event.clear()
        match self.mode:
            case '6DoF':
                self.output.append("Начата запись... режим 6DoF 1000 Hz")
                self.MPUInterface.write((2).to_bytes(1, byteorder="big"))
            case '9DoF':
                self.output.append("Начата запись... режим 9DoF ~900 Hz")
                self.MPUInterface.write((4).to_bytes(1, byteorder="big"))
        self.recorder_thread = Thread(target=self.recorder)
        self.recorder_thread.start()

    def stop_recording(self):
        self.MPUInterface.write((1).to_bytes(1, byteorder="big"))
        self.pause_event.set()
        self.recorder_thread.join()
        self.output.append("Запись остановлена")
        DF_savename = os.path.join(self.savepath, 'Single_' + datetime.now().strftime("%Y%m%d_%H%M%S") + '.h5')
        Data_df = pd.DataFrame({'SystemTime': self.datetime_list,
                                'MPU1_data': self.MPUdata})
        Data_df.to_hdf(DF_savename, key='data', index=False)
        self.output.append("Данные сохранены")
