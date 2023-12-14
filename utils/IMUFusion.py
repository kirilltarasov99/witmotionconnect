from utils.filters import Madgwick, IMUFusion


name = '/home/mikulel/Документы/labADT/witmotionconnect/Single_20231103_164036_deciphered.csv'
filter = Madgwick()
fusion = IMUFusion(filter, name)
fusion.IMUFusion()
print('KALMAN')
acc = fusion.KalmanAcc()
print('KALMAN end')
fusion.save_kalman_acc(acc)
fusion.save_quats_txt()
fusion.save_YPR_txt()
