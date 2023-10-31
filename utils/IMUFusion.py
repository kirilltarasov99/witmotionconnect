from utils.filters import Madgwick, IMUFusion


name = '/home/mikulel/Документы/labADT/witmotionconnect/Single_20231030_131915_deciphered.csv'
filter = Madgwick()
fusion = IMUFusion(filter, name)
fusion.IMUFusion()
fusion.save_quats_txt()
fusion.save_YPR_txt()
