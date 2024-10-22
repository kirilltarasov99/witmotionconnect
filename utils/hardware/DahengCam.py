import gxipy as gx
import cv2 as cv
import os
import threading

from pathlib import Path, PurePath
from datetime import datetime
from threading import Thread, Event


class DahengCapture(object):
    def __init__(self, QToutput, savepath, frameSize, fps):
        self.output = QToutput
        self.savepath = savepath
        self.cap = None
        self.recorder_thread = None
        self.frame_list1 = []
        self.time_list1 = []
        self.frame_list2 = []
        self.time_list2 = []
        self.pause_event = Event()
        self.out = cv.VideoWriter
        self.device_manager = gx.DeviceManager()
        dev_num, self.dev_info_list = self.device_manager.update_device_list()
        if dev_num == 0:
            raise Exception("No Daheng camera found!")
    
    def create_videowriter(self, cam_id):
            return True

    def connect(self, cam_address, cam_id='cam1'):
        if os.name == 'nt':
            self.output.append('Данный тип камер не работает на Windows')
            raise Exception("Данный тип камер не работает на Windows")
        
        else:
            self.address = cam_address
            self.cap = self.device_manager.open_device_by_sn(self.address)
            try:
                self.cam_id = cam_id
                self.output.append('Камера подключена')
                if self.cap.DeviceModelName.is_implemented():
                    self.output.append('Модель камеры: ' + self.cap.DeviceModelName.get())
                
                if self.cap.SensorWidth.is_implemented() and self.cap.SensorHeight.is_implemented():
                    self.output.append('Разрешение: ' + str(self.cap.SensorWidth.get()) + 'x' + str(self.cap.SensorHeight.get()))

            except Exception as e:
                self.output.append(f'Ошибка при подключении к камере: {e}')
            
    def record_frame(self, start_time, timestamp, image):
        data_path = Path(PurePath(self.savepath, self.cam_id + 'video' + start_time))
        if not data_path.is_dir():
            data_path.mkdir()
        cv.imwrite(str(PurePath(data_path, 'frame' + timestamp.strftime('%Y%m%d_%H%M%S.%f')[:-3] + '.png')), image)

    def recorder(self):
        start_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        while True:
            if self.pause_event.is_set():
                break

            raw_image = self.cap.data_stream[0].get_image()
            if raw_image.get_status() == gx.GxFrameStatusList.INCOMPLETE:
                print("incomplete frame")
            
            else:
                timestamp = datetime.now()
                numpy_image = raw_image.get_numpy_array()
                threading.Thread(target=self.record_frame, args=(start_time, timestamp, numpy_image, )).start()

    def start_recording(self, cam_id):
        self.out = self.create_videowriter(cam_id)
        self.cam_id = cam_id
        self.cap.stream_on()
        self.pause_event.clear()
        self.recorder_thread = Thread(target=self.recorder)
        self.recorder_thread.start()

    def stop_recording(self):
        self.pause_event.set()
        self.recorder_thread.join()
        self.cap.stream_off()
    
    def disconnect(self):
        self.cap.close_device()