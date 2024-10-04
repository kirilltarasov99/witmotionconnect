import gxipy as gx
import cv2 as cv
import os
import numpy as np

from pathlib import PurePath
from datetime import datetime
from threading import Thread, Event


class DahengCapture(object):
    def __init__(self, QToutput, savepath, frameSize, fps):
        self.output = QToutput
        self.savepath = savepath
        self.cap = None
        self.recorder_thread = None
        self.pause_event = Event()
        self.out = cv.VideoWriter
        self.device_manager = gx.DeviceManager()
        dev_num, self.dev_info_list = self.device_manager.update_device_list()
        if dev_num == 0:
            raise Exception("No Daheng camera found!")
    
    def create_videowriter(self, cam_id):
        if os.name == 'nt':
            return cv.VideoWriter(str(PurePath(self.savepath, 'CameraVideo_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.avi')),
                                  fourcc=cv.VideoWriter.fourcc(*'mp4v'),
                                  fps=self.cap.get(cv.CAP_PROP_FPS),
                                  frameSize=[int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))])
        else:
            return cv.VideoWriter(str(PurePath(self.savepath, cam_id + '_video_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.avi')),
                                  fourcc=cv.VideoWriter.fourcc(*'XVID'),
                                  fps=19.6,
                                  frameSize=(5496, 3672))

    def connect(self, cam_address):
        if os.name == 'nt':
            self.output.append('Данный тип камер не работает на Windows')
            raise Exception("Данный тип камер не работает на Windows")
        
        else:
            self.address = cam_address
            self.cap = self.device_manager.open_device_by_sn(self.address)
            try:
                self.output.append('Камера подключена')
                if self.cap.DeviceModelName.is_implemented():
                    self.output.append('Модель камеры: ' + self.cap.DeviceModelName.get())
                
                if self.cap.SensorWidth.is_implemented() and self.cap.SensorHeight.is_implemented():
                    self.output.append('Разрешение: ' + str(self.cap.SensorWidth.get()) + 'x' + str(self.cap.SensorHeight.get()))

            except Exception as e:
                self.output.append(f'Ошибка при подключении к камере: {e}')
            
    def recorder(self):
        while True:
            if self.pause_event.is_set():
                break

            raw_image = self.cap.data_stream[0].get_image()
            if raw_image.get_status() == gx.GxFrameStatusList.INCOMPLETE:
                print("incomplete frame")
            
            else:
                numpy_image = raw_image.get_numpy_array()
                self.out.write(cv.cvtColor(numpy_image, cv.COLOR_RGB2BGR))

        self.out.release()

    def start_recording(self, cam_id):
        self.out = self.create_videowriter(cam_id)
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