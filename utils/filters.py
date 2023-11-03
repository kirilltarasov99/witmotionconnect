import numpy as np
import pandas as pd
from datetime import datetime
import math
from pykalman import KalmanFilter


class Madgwick:
    def __init__(self):
        self.q = [1., 0., 0., 0.]
        self.beta = np.sqrt(3/4) * math.pi * (40/180)
        self.zeta = np.sqrt(3/4) * math.pi * (0/180)

    def get_quaternion(self, data, deltat):
        ax, ay, az, gx, gy, gz, mx, my, mz = data
        q1, q2, q3, q4 = self.q

        _2q1 = 2.0 * q1
        _2q2 = 2.0 * q2
        _2q3 = 2.0 * q3
        _2q4 = 2.0 * q4
        _2q1q3 = 2.0 * q1 * q3
        _2q3q4 = 2.0 * q3 * q4
        q1q1 = q1 * q1
        q1q2 = q1 * q2
        q1q3 = q1 * q3
        q1q4 = q1 * q4
        q2q2 = q2 * q2
        q2q3 = q2 * q3
        q2q4 = q2 * q4
        q3q3 = q3 * q3
        q3q4 = q3 * q4
        q4q4 = q4 * q4

        # Normalise accelerometer measurement
        norm = np.sqrt(ax * ax + ay * ay + az * az)
        if norm == 0:
            print('Normalised accelerometer measurement is 0')
            return

        norm = 1 / norm
        ax *= norm
        ay *= norm
        az *= norm

        # Normalise magnetometer measurement
        norm = np.sqrt(mx * mx + my * my + mz * mz)
        if norm == 0:
            print('Normalised magnetometer measurement is 0')
            return

        norm = 1 / norm
        mx *= norm
        my *= norm
        mz *= norm

        # Reference direction of Earth's magnetic field
        _2q1mx = _2q1 * mx
        _2q1my = _2q1 * my
        _2q1mz = _2q1 * mz
        _2q2mx = _2q2 * mx

        hx = mx * q1q1 - _2q1my * q4 + _2q1mz * q3 + mx * q2q2 + _2q2 * my * q3 + _2q2 * mz * q4 - mx * q3q3 - mx * q4q4
        hy = _2q1mx * q4 + my * q1q1 - _2q1mz * q2 + _2q2mx * q3 - my * q2q2 + my * q3q3 + _2q3 * mz * q4 - my * q4q4

        _2bx = np.sqrt(hx * hx + hy * hy)
        _2bz = -_2q1mx * q3 + _2q1my * q2 + mz * q1q1 + _2q2mx * q4 - mz * q2q2 + _2q3 * my * q4 - mz * q3q3 + mz * q4q4

        _4bx = 2 * _2bx
        _4bz = 2 * _2bz

        # Gradient decent algorithm corrective step
        s1 = -_2q3 * (2 * q2q4 - _2q1q3 - ax) + _2q2 * (2 * q1q2 + _2q3q4 - ay) - _2bz * q3 * (
                _2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q4 + _2bz * q2) * (
                     _2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + _2bx * q3 * (
                     _2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)

        s2 = _2q4 * (2 * q2q4 - _2q1q3 - ax) + _2q1 * (2 * q1q2 + _2q3q4 - ay) - 4 * q2 * (
                    1 - 2 * q2q2 - 2 * q3q3 - az) + _2bz * q4 * (
                     _2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (_2bx * q3 + _2bz * q1) * (
                     _2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + (_2bx * q4 - _4bz * q2) * (
                     _2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)

        s3 = -_2q1 * (2 * q2q4 - _2q1q3 - ax) + _2q4 * (2 * q1q2 + _2q3q4 - ay) - 4 * q3 * (
                    1 - 2 * q2q2 - 2 * q3q3 - az) + (-_4bx * q3 - _2bz * q1) * (
                     _2bx * (0 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (_2bx * q2 + _2bz * q4) * (
                     _2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + (_2bx * q1 - _4bz * q3) * (
                     _2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)

        s4 = _2q2 * (2 * q2q4 - _2q1q3 - ax) + _2q3 * (2 * q1q2 + _2q3q4 - ay) + (-_4bx * q4 + _2bz * q2) * (
                _2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q1 + _2bz * q3) * (
                     _2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + _2bx * q2 * (
                     _2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)

        norm = np.sqrt(s1 * s1 + s2 * s2 + s3 * s3 + s4 * s4)
        norm = 1 / norm
        s1 *= norm
        s2 *= norm
        s3 *= norm
        s4 *= norm

        # Compute rate of change of quaternion
        qDot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) - self.beta * s1
        qDot2 = 0.5 * (q1 * gx + q3 * gz - q4 * gy) - self.beta * s2
        qDot3 = 0.5 * (q1 * gy - q2 * gz + q4 * gx) - self.beta * s3
        qDot4 = 0.5 * (q1 * gz + q2 * gy - q3 * gx) - self.beta * s4

        # Integrate to yield quaternion
        q1 += qDot1 * deltat
        q2 += qDot2 * deltat
        q3 += qDot3 * deltat
        q4 += qDot4 * deltat

        norm = np.sqrt(q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4)  # normalise quaternion
        norm = 1 / norm
        self.q[0] = q1 * norm
        self.q[1] = q2 * norm
        self.q[2] = q3 * norm
        self.q[3] = q4 * norm

    def get_earth_acceleration(self, acceleration):
        q1, q2, q3, q4 = self.q
        ax, ay, az = acceleration
        q1q1 = q1 * q1
        q1q2 = q1 * q2
        q1q3 = q1 * q3
        q1q4 = q1 * q4
        q2q3 = q2 * q3
        q2q4 = q2 * q4
        q3q4 = q3 * q4

        earth_acceleration = [2 * ((q1q1 - 0.5 + q2 * q2) * ax + (q2q3 - q1q4) * ay + (q2q4 + q1q3) * az),
                              2 * ((q2q3 + q1q4) * ax + (q1q1 - 0.5 + q3 * q3) * ay + (q3q4 - q1q2) * az),
                              2 * ((q2q4 - q1q3) * ax + (q3q4 + q1q2) * ay + (q1q1 - 0.5 + q4 * q4) * az) - 1]

        return earth_acceleration


class IMUFusion:
    def __init__(self, algo, file_name):
        self.algo = algo
        self.file_name = file_name
        self.df = self.parse_file()
        self.timestamps = self.get_timestamps()
        self.accX = self.df['ax_MPU1']
        self.accY = self.df['ay_MPU1']
        self.accZ = self.df['az_MPU1']
        self.gyrX = self.df['gx_MPU1']
        self.gyrY = self.df['gy_MPU1']
        self.gyrZ = self.df['gz_MPU1']
        self.magX = self.df['mx_MPU1']
        self.magY = self.df['my_MPU1']
        self.magZ = self.df['mz_MPU1']
        self.quaternions = []
        self.earth_acceleration = []
        self.YPR = []

    def parse_file(self):
        if self.file_name[-3:] == 'csv':
            print('csv')
            df = pd.read_csv(self.file_name)
        elif self.file_name[-2:] == 'h5':
            print('h5')
            df = pd.read_hdf(self.file_name, key='data')
        else:
            print('Unknown type')
            return
        return df

    def get_timestamps(self):
        timestamps = list(map(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f"), list(self.df['SystemTime'])))
        timestamps = [timestamp.timestamp() for timestamp in timestamps]
        return timestamps

    def IMUFusion(self):
        for i in range(len(self.timestamps)):
            if i > 0:
                time_passed = self.timestamps[i] - self.timestamps[i - 1]
            else:
                time_passed = 0.001
            deltat = time_passed / 10
            for j in range(10):
                self.algo.get_quaternion((self.accX[i], self.accY[i], self.accZ[i],
                                  self.gyrX[i] * math.pi / 180, self.gyrY[i] * math.pi / 180, self.gyrZ[i] * math.pi / 180,
                                  self.magY[i], self.magX[i], self.magZ[i]), deltat)

            self.quaternions.append(self.algo.q.copy())
            self.earth_acceleration.append(self.algo.get_earth_acceleration())

    @staticmethod
    def quats_toYPR(q):
        yaw = math.atan2(2 * (q[1] * q[2] + q[0] * q[3]), q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3])
        pitch = -math.asin(2 * (q[1] * q[3] - q[0] * q[2]))
        roll = math.atan2(2 * (q[0] * q[1] + q[2] * q[3]), q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3])
        pitch *= 180 / math.pi
        yaw *= 180 / math.pi
        yaw -= 8.1439  # magnetic declination @ NSU 24.10.2023
        roll *= 180 / math.pi
        return [yaw, pitch, roll]

    def save_quats_txt(self):
        np.savetxt(self.file_name[:-4]+'_quats.txt', self.quaternions)

    def save_YPR_txt(self):
        for quat in self.quaternions:
            self.YPR.append(self.quats_toYPR(quat))
        np.savetxt(self.file_name[:-4]+'_YPR.txt', self .YPR)
