# Daheng Imaging-2BA200004094-FCG23081373
# might require export GI_TYPELIB_PATH=/usr/local/lib64/girepository-1.0 before using
from .aravis import Camera as AravisCamera
import cv2 as cv
import os
import numpy as np
from pathlib import PurePath
from datetime import datetime
from threading import Thread, Event


class AravisCapture(object):
    def __init__(self, QToutput, savepath, frameSize, fps):
        self.output = QToutput
        self.savepath = savepath
        self.cap = None
        self.recorder_thread = None
        self.pause_event = Event()
        self.out = cv.VideoWriter

    def create_videowriter(self):
        if os.name == 'nt':
            return cv.VideoWriter(str(PurePath(self.savepath, 'CameraVideo_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.avi')),
                                  fourcc=cv.VideoWriter.fourcc(*'mp4v'),
                                  fps=self.cap.get(cv.CAP_PROP_FPS),
                                  frameSize=[int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))])
        else:
            return cv.VideoWriter(str(PurePath(self.savepath, 'CameraVideo_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.avi')),
                                  fourcc=cv.VideoWriter.fourcc(*'XVID'),
                                  fps=15,
                                  frameSize=[5496, 3672])

    def connect(self, cam_address):
        if os.name == 'nt':
            self.output.append('Данный тип камер не работает на Windows')
        
        else:
            self.cap = AravisCamera(cam_address)
            try:
                self.output.append('Камера подключена')
                self.output.append('Модель камеры: '+self.cap.get_model_name())
            except Exception as e:
                self.output.append(f'Ошибка при подключении к камере: {e}')
            
    def recorder(self):
        while True:
            if self.pause_event.is_set():
                break

            frame = self.cap.pop_frame()
            
            self.out.write(cv.cvtColor(frame, cv.COLOR_RGB2BGR))

    def start_recording(self):
        self.out = self.create_videowriter()
        self.cap.start_acquisition_continuous()
        self.pause_event.clear()
        self.recorder_thread = Thread(target=self.recorder)
        self.recorder_thread.start()

    def stop_recording(self):
        self.pause_event.set()
        self.recorder_thread.join()
        self.out.release()
        self.output.append('Запись остановлена')
    
    def disconnect(self):
        self.cap.shutdown()
