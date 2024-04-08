import os
if os.name == 'nt':
    os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2 as cv
from pathlib import PurePath
from datetime import datetime
from threading import Thread, Event


class VideoCapture(object):
    """
                :NOTE:
                    Class for communication with a V4L2 capture card.

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
        if os.name == 'nt':
            vid_savename = PurePath(self.savepath, 'Video_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.mp4')
            self.out = cv.VideoWriter(str(vid_savename), fourcc=cv.VideoWriter.fourcc(*'mp4v'),
                                      fps=self.cap.get(cv.CAP_PROP_FPS), frameSize=self.frameSize)
        else:
            vid_savename = PurePath(self.savepath, 'Video_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.avi')
            self.out = cv.VideoWriter(str(vid_savename), fourcc=cv.VideoWriter.fourcc(*'XVID'),
                                      fps=self.cap.get(cv.CAP_PROP_FPS), frameSize=self.frameSize)
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
        """
                    :NOTE:
                        Releases capture card from use in the app.
        """

        self.cap.release()
