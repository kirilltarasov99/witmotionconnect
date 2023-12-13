from witmotion import IMU
import time
import witmotion.protocol
import pandas as pd
from datetime import datetime


class WitMotionDialog:
    def __init__(self, QToutput, savepath):
        self.output = QToutput
        self.savepath = savepath
        self.recording = False
        self.data_dict = {}
        self.imu = None
        self.IMUdata = None

    def connect(self, port, baud_rate):
        self.imu = IMU(path=port, baudrate=baud_rate)
        time.sleep(1)
        chiptime = self.imu.get_timestamp()
        if chiptime is None:
            self.output.append("Выбранный baud rate некорректен, отключите датчик и повторите подключение")
        else:
            self.recording = False
            self.output.append("Датчик подключен")
            self.imu.subscribe(self.callback)

    def disconnect(self):
        self.imu.close()
        self.output.append("Датчик отключен")

    def start_recording(self):
        self.output.append("Начата запись")
        self.create_df()
        self.recording = True

    def stop_recording(self):
        self.output.append("Запись остановлена")
        self.recording = False
        DF_savename = datetime.now().strftime("%Y%m%d_%H%M%S") + '.csv'
        self.IMUdata.to_csv(DF_savename, sep='\t', index=False)

# Following functions are called only locally
    def callback(self, msg):
        if type(msg) is witmotion.protocol.TimeMessage:
            ChipTime = self.imu.get_timestamp()
            SystemTime = datetime.now()
            self.data_dict.update({'ChipTime': datetime.fromtimestamp(ChipTime)})
            self.data_dict.update({'SystemTime': SystemTime})

        elif type(msg) is witmotion.protocol.AccelerationMessage:
            AccelerationVector = self.imu.get_acceleration()
            if AccelerationVector is None:
                AccelerationVector = (0, 0, 0)
            self.data_dict.update({'ax(g)': AccelerationVector[0]})
            self.data_dict.update({'ay(g)': AccelerationVector[1]})
            self.data_dict.update({'az(g)': AccelerationVector[2]})

        elif type(msg) is witmotion.protocol.AngularVelocityMessage:
            AngularVector = self.imu.get_angular_velocity()
            if AngularVector is None:
                AngularVector = (0, 0, 0)
            self.data_dict.update({'wx(deg/s)': AngularVector[0]})
            self.data_dict.update({'wy(deg/s)': AngularVector[1]})
            self.data_dict.update({'wz(deg/s)': AngularVector[2]})

            if self.recording is True:
                self.IMUdata.loc[len(self.IMUdata)] = self.data_dict

    def create_df(self):
        self.IMUdata = pd.DataFrame(columns=['SystemTime', 'ChipTime', 'ax(g)', 'ay(g)', 'az(g)', 'wx(deg/s)', 'wy(deg/s)', 'wz(deg/s)'])
