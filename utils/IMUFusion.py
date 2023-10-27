import numpy as np

from utils.Filters import FilterAlgo
import pandas as pd
import math
from datetime import datetime


def convert_toYPR(q):
    yaw = math.atan2(2 * (q[1] * q[2] + q[0] * q[3]), q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3])
    pitch = -math.asin(2 * (q[1] * q[3] - q[0] * q[2]))
    roll = math.atan2(2 * (q[0] * q[1] + q[2] * q[3]), q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3])
    pitch *= 180 / math.pi
    yaw *= 180 / math.pi
    yaw -= 8.1439  # magnetic declination @ NSU 24.10.2023
    roll *= 180 / math.pi
    return [yaw, pitch, roll]


data = pd.read_csv('../Single_20231027_161730_deciphered.csv')
timestamps = list(map(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f"), list(data['SystemTime'])))
timestamps = [timestamp.timestamp() for timestamp in timestamps]
accX = data['ax_MPU1']
accY = data['ay_MPU1']
accZ = data['az_MPU1']
gyrX = data['gx_MPU1']
gyrY = data['gy_MPU1']
gyrZ = data['gz_MPU1']
magX = data['mx_MPU1']
magY = data['my_MPU1']
magZ = data['mz_MPU1']

quaternions = []
angles = []

CurFilter = FilterAlgo()

GyroMeasError = math.pi * (40/180)
GyroMeasDrift = math.pi * (0/180)
beta = np.sqrt(3/4) * GyroMeasError
zeta = np.sqrt(3/4) * GyroMeasDrift

for i in range(len(timestamps)):
    if i > 0:
        time_passed = timestamps[i] - timestamps[i-1]
    else:
        time_passed = 0.001
    deltat = time_passed / 10
    for j in range(10):
        CurFilter.Madgwick((accX[i], accY[i], accZ[i], gyrX[i]*math.pi/180, gyrY[i]*math.pi/180, gyrZ[i]*math.pi/180, magY[i], magX[i], magZ[i]),
                           beta, deltat)
    quaternions.append(CurFilter.q.copy())

np.savetxt('quats.txt', quaternions)
for i in range(len(quaternions)):
    angles.append(convert_toYPR(quaternions[i]))

np.savetxt('angles.txt', angles)
