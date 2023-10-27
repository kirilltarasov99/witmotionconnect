from utils.filters import Madgwick, IMUFusion
import pandas as pd
import math


def convert_toYPR(q):
    yaw = math.atan2(2 * (q[1] * q[2] + q[0] * q[3]), q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3])
    pitch = -math.asin(2 * (q[1] * q[3] - q[0] * q[2]))
    roll = math.atan2(2 * (q[0] * q[1] + q[2] * q[3]), q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3])
    pitch *= 180 / math.pi
    yaw *= 180 / math.pi
    yaw -= 8.1439  # magnetic declination @ NSU 24.10.2023
    roll *= 180 / math.pi
    return [yaw, pitch, roll]


name = '/home/mikulel/Документы/labADT/witmotionconnect/Single_20231027_161730_deciphered.csv'
filter = Madgwick()
fusion = IMUFusion(filter, name)
fusion.IMUFusion()
fusion.save_YPR_txt()


