import serial
import pandas as pd

from datetime import datetime
from threading import Thread, Event
from time import sleep, perf_counter


class SingleMPUDialog:
    def __init__(self, output):
        self.output = output
        self.recording = False
        self.datetime_list = []
        self.MPUInterface = None
        self.MPUdata = []
        self.pause_event = Event()
        self.recorder_thread = Thread(target=self.recorder)

    def connect(self, port, baud_rate):
        self.MPUInterface = serial.Serial(port=port, baudrate=baud_rate)
        self.recording = False
        self.output.append("Датчик подключен")

    def disconnect(self):
        self.MPUInterface.close()
        self.output.append("Датчик отключен")

    def recorder(self):
        if self.MPUInterface.is_open is True:
            if self.recording is True:
                self.MPUInterface.reset_input_buffer()
                sleep(0.005)
                self.MPUInterface.write((3).to_bytes(1, byteorder="big"))
                self.output.append('Инициализация; режим 9DoF')
                sleep(0.00045)
                init_time_stop = perf_counter() + 1
                while perf_counter() < init_time_stop:
                    self.datetime_list.append(datetime.now())
                    self.MPUdata.append(self.MPUInterface.read(18))

                self.MPUInterface.write((2).to_bytes(1, byteorder="big"))
                self.output.append('Инициализация закончена, режим 6DoF')

        while self.MPUInterface.is_open is True:
            if self.pause_event.is_set():
                break
            if self.recording is True:
                self.datetime_list.append(datetime.now())
                self.MPUdata.append(self.MPUInterface.read(18))

    def start_recording(self):
        self.recording = True
        self.MPUdata = []
        self.datetime_list = []
        self.pause_event.clear()
        self.recorder_thread.start()
        self.output.append("Начата запись")

    def stop_recording(self):
        self.recording = False
        self.MPUInterface.write((1).to_bytes(1, byteorder="big"))
        self.pause_event.set()
        self.recorder_thread.join()
        self.output.append("Запись остановлена")
        DF_savename = 'Single_' + datetime.now().strftime("%Y%m%d_%H%M%S") + '.h5'
        Data_df = pd.DataFrame({'SystemTime': self.datetime_list,
                                'MPU1_data': self.MPUdata})
        Data_df.to_hdf(DF_savename, key='data', index=False)
        self.output.append("Данные сохранены")
