import serial
import pandas as pd

from datetime import datetime
from threading import Thread, Event
from time import sleep


class SingleMPUDialog:
    def __init__(self, output):
        self.output = output
        self.recording = False
        self.datetime_list = []
        self.MPUInterface = None
        self.MPUdata = []
        self.AccData = []
        self.GyrData = []
        self.MagData = []
        self.pause_event = Event()
        self.recorder_thread = Thread(target=self.recorder_9DoF_fast)
        self.hasStarted = bool(False)

    def connect(self, port, baud_rate):
        self.MPUInterface = serial.Serial(port=port, baudrate=baud_rate)
        self.recording = False
        self.output.append("Датчик подключен")

    def disconnect(self):
        self.MPUInterface.close()
        self.output.append("Датчик отключен")

    def recorder_9DoF_fast(self):
        self.MPUInterface.reset_input_buffer()
        sleep(0.005)
        while self.MPUInterface.is_open is True:
            if self.pause_event.is_set():
                self.MPUInterface.reset_input_buffer()
                break
            if self.recording is True:
                self.MPUInterface.write((4).to_bytes(1, byteorder="big"))
                sleep(0.00045)
                self.datetime_list.append(datetime.now())
                self.MPUdata.append(self.MPUInterface.read(18))

    def start_recording(self):
        self.recording = True
        self.MPUdata = []
        self.datetime_list = []
        self.pause_event.clear()
        if self.hasStarted is False:
            self.recorder_thread.start()
            self.hasStarted = True
        self.output.append("Начата запись... режим 9DoF ~900 Hz")

    def stop_recording(self):
        self.MPUInterface.write((1).to_bytes(1, byteorder="big"))
        self.recording = False
        self.pause_event.set()
        self.recorder_thread.join()
        self.output.append("Запись остановлена")
        DF_savename = 'Single_' + datetime.now().strftime("%Y%m%d_%H%M%S") + '.h5'
        Data_df = pd.DataFrame({'SystemTime': self.datetime_list,
                                'MPU1_data': self.MPUdata})
        Data_df.to_hdf(DF_savename, key='data', index=False)
        self.output.append("Данные сохранены")
