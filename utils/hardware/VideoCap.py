import os
if os.name == 'nt':
    os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2 as cv
import numpy as np
from pathlib import PurePath
from datetime import datetime
import threading
import queue


class VideoCapture(object):
    """
                :NOTE:
                    Class for communication with a capture card.

                :args:
                    QToutput (QTextEdit): GUI object for output messages
                    savepath (pathlib.Path): path to data folder
                    frameSize (list): video resolution
                    fps (string): fps of video
    """

    def __init__(self, QToutput, savepath, frameSize, fps):
        self.cap = cv.VideoCapture
        self.output = QToutput
        self.savepath = savepath
        self.timestamps = []

        self.fps = int(fps)
        self.frameSize = [eval(i) for i in frameSize]

        self.recorder_thread = None
        self.pause_event = threading.Event()
        self.threadlock = threading.Lock()
        self.out = cv.VideoWriter
    
    def create_videowriter(self):
        """
                    :NOTE:
                        Creates VideoWriter.
        """

        if os.name == 'nt':
            return cv.VideoWriter(str(PurePath(self.savepath, 'USVideo_' + datetime.now().strftime('%Y%m%d_%H%M%S.%f') + '.avi')),
                                  fourcc=cv.VideoWriter.fourcc(*'mp4v'),
                                  fps=self.cap.get(cv.CAP_PROP_FPS),
                                  frameSize=[int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))])
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S.%f')[:-3]
            self.savename = str(PurePath(self.savepath, 'USVideo_timestamps' + timestamp + '.npz'))
            self.out = cv.VideoWriter(str(PurePath(self.savepath, 'USVideo_' + timestamp + '.avi')),
                                  fourcc=cv.VideoWriter.fourcc(*'XVID'),
                                  fps=self.cap.get(cv.CAP_PROP_FPS),
                                  frameSize=[int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))])

    def connect(self, cam_address):
        """
                    :NOTE:
                        Opens connection to capture card and creates VideoWriter.

                    :args:
                        cam_address (string): address of capture card
        """

        if os.name == 'nt':
            self.cap = cv.VideoCapture(int(cam_address), cv.CAP_DSHOW)
        else:
            self.cap = cv.VideoCapture(cam_address)
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, self.frameSize[0])
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.frameSize[1])
        self.cap.set(cv.CAP_PROP_FPS, self.fps)

        if self.cap.isOpened():
            self.output.append('Рекордер подключен')
            self.output.append('Разрешение: ' + str(self.cap.get(cv.CAP_PROP_FRAME_WIDTH)) +
                               'x' + str(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT)))
            self.output.append('FPS: ' + str(self.cap.get(cv.CAP_PROP_FPS)))

        else:
            self.output.append('Проблема при подключении рекордера')

    def record_frame(self, queue):
        while True:
            frame, timestamp = queue.get()
            self.out.write(frame)
            self.timestamps.append(timestamp)
            queue.task_done()

    def recorder(self):
        """
                    :NOTE:
                        Records frames from capture card into a video file.
        """
        record_queue = queue.Queue()
        threading.Thread(target=self.record_frame, args=(record_queue,), daemon=True).start()
        while self.cap.isOpened():
            if self.pause_event.is_set():
                break

            ret, frame = self.cap.read()
            if not ret:
                print('Ошибка в получении кадра. Проверьте рекордер и начните сначала')
                break
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S.%f')[:-3]
            record_queue.put((frame, timestamp))
        record_queue.join()

    def start_recording(self, start_recorder):
        """
                    :NOTE:
                        Starts recording data.
        """

        self.timestamps = []
        self.create_videowriter()
        if start_recorder:
            self.pause_event.clear()
            self.recorder_thread = threading.Thread(target=self.recorder)
            self.recorder_thread.start()

    def stop_recording(self, stop_recorder):
        """
                    :NOTE:
                        Stops recording data.
        """

        if stop_recorder:
            self.pause_event.set()
            self.recorder_thread.join()
        self.out.release()
        np.savez(self.savename, timestamps=self.timestamps)
        self.output.append('Рекордер остановлен')

    def disconnect(self):
        """
                    :NOTE:
                        Releases capture card from use in the app.
        """

        self.cap.release()
