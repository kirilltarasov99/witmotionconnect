import cv2 as cv

from pathlib import PurePath
from datetime import datetime
from threading import Thread, Event


class VideoCapture(object):
    def __init__(self, QToutput, savepath, frameSize, fps):
        self.cap = cv.VideoCapture
        self.output = QToutput
        self.savepath = savepath

        self.fps = int(fps)
        self.frameSize = [eval(i) for i in frameSize]

        self.recorder_thread = None
        self.pause_event = Event()
        self.out = cv.VideoWriter

    def connect(self, cam_address):
        """
                    :NOTE:
                        Opens connection to capture card and creates VideoWriter.

                    :args:
                        port (string): serial port address
                        baud_rate (string): baud rate value
        """
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

    def recorder(self):
        """
                    :NOTE:
                        Records frames from capture card into a video file.
        """

        while self.cap.isOpened():
            if self.pause_event.is_set():
                break

            ret, frame = self.cap.read()
            if not ret:
                print('Ошибка в получении кадра. Проверьте рекордер и начните сначала')
                break
            self.out.write(frame)

    def start_recording(self):
        """
                    :NOTE:
                        Starts recording data.
        """
        vid_savename = PurePath(self.savepath, 'Video_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.avi')
        self.out = cv.VideoWriter(str(vid_savename), fourcc=cv.VideoWriter.fourcc(*'XVID'),
                                  fps=self.fps, frameSize=self.frameSize)
        self.pause_event.clear()
        self.recorder_thread = Thread(target=self.recorder)
        self.recorder_thread.start()

    def stop_recording(self):
        """
                    :NOTE:
                        Stops recording data.
        """

        self.pause_event.set()
        self.recorder_thread.join()
        self.out.release()
        self.output.append('Рекордер остановлен')

    def disconnect(self):
        self.cap.release()
