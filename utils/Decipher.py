import pandas as pd


class Decipher:
    def __init__(self):
        self.table = pd.DataFrame
        self.ax_MPU1_list = []
        self.ay_MPU1_list = []
        self.az_MPU1_list = []
        self.gx_MPU1_list = []
        self.gy_MPU1_list = []
        self.gz_MPU1_list = []
        self.ax_MPU2_list = []
        self.ay_MPU2_list = []
        self.az_MPU2_list = []
        self.gx_MPU2_list = []
        self.gy_MPU2_list = []
        self.gz_MPU2_list = []

    def open(self, file_name):
        self.table = pd.read_hdf(file_name[0], key='data')

    def decipher(self, acc_range, gyro_range):
        print('Дешифрование...')
        if 'MPU1_data' in self.table.columns:
            for i in range(len(self.table['MPU1_data'])):
                ax = int.from_bytes(self.table['MPU1_data'][i][:2], byteorder='little', signed=True)
                ay = int.from_bytes(self.table['MPU1_data'][i][2:4], byteorder='little', signed=True)
                az = int.from_bytes(self.table['MPU1_data'][i][4:6], byteorder='little', signed=True)
                if acc_range == '2g':
                    ax /= 16384
                    ay /= 16384
                    az /= 16384
                elif acc_range == '4g':
                    ax /= 8192
                    ay /= 8192
                    az /= 8192
                elif acc_range == '8g':
                    ax /= 4096
                    ay /= 4096
                    az /= 4096
                elif acc_range == '16g':
                    ax /= 2048
                    ay /= 2048
                    az /= 2048
                self.ax_MPU1_list.append(ax)
                self.ay_MPU1_list.append(ay)
                self.az_MPU1_list.append(az)

                gx = int.from_bytes(self.table['MPU1_data'][i][6:8], byteorder='little', signed=True)
                gy = int.from_bytes(self.table['MPU1_data'][i][8:10], byteorder='little', signed=True)
                gz = int.from_bytes(self.table['MPU1_data'][i][10:12], byteorder='little', signed=True)
                if acc_range == '2g':
                    gx /= 16384
                    gy /= 16384
                    gz /= 16384
                elif acc_range == '4g':
                    gx /= 8192
                    gy /= 8192
                    gz /= 8192
                elif acc_range == '8g':
                    gx /= 4096
                    gy /= 4096
                    gz /= 4096
                elif acc_range == '16g':
                    gx /= 2048
                    gy /= 2048
                    gz /= 2048

                self.gx_MPU1_list.append(gx)
                self.gy_MPU1_list.append(gy)
                self.gz_MPU1_list.append(gz)

        if 'MPU2_data' in self.table.columns:
            for i in range(len(self.table['MPU2_data'])):
                ax = int.from_bytes(self.table['MPU2_data'][i][:2], byteorder='little', signed=True)
                ay = int.from_bytes(self.table['MPU2_data'][i][2:4], byteorder='little', signed=True)
                az = int.from_bytes(self.table['MPU2_data'][i][4:6], byteorder='little', signed=True)
                if acc_range == '2g':
                    ax /= 16384
                    ay /= 16384
                    az /= 16384
                elif acc_range == '4g':
                    ax /= 8192
                    ay /= 8192
                    az /= 8192
                elif acc_range == '8g':
                    ax /= 4096
                    ay /= 4096
                    az /= 4096
                elif acc_range == '16g':
                    ax /= 2048
                    ay /= 2048
                    az /= 2048
                self.ax_MPU2_list.append(ax)
                self.ay_MPU2_list.append(ay)
                self.az_MPU2_list.append(az)

                gx = int.from_bytes(self.table['MPU2_data'][i][6:8], byteorder='little', signed=True)
                gy = int.from_bytes(self.table['MPU2_data'][i][8:10], byteorder='little', signed=True)
                gz = int.from_bytes(self.table['MPU2_data'][i][10:12], byteorder='little', signed=True)
                if acc_range == '2g':
                    gx /= 16384
                    gy /= 16384
                    gz /= 16384
                elif acc_range == '4g':
                    gx /= 8192
                    gy /= 8192
                    gz /= 8192
                elif acc_range == '8g':
                    gx /= 4096
                    gy /= 4096
                    gz /= 4096
                elif acc_range == '16g':
                    gx /= 2048
                    gy /= 2048
                    gz /= 2048

                self.gx_MPU2_list.append(gx)
                self.gy_MPU2_list.append(gy)
                self.gz_MPU2_list.append(gz)
        else:
            print('Неизвестный формат таблицы')
            return

    def save(self, file_name, table_format):
        if 'MPU2_data' in self.table.columns:
            presave_df = pd.DataFrame({'SystemTime': self.table['SystemTime'],
                                       'ax_MPU1': self.ax_MPU1_list, 'ay_MPU1': self.ay_MPU1_list,
                                       'az_MPU1': self.az_MPU1_list, 'gx_MPU1': self.gx_MPU1_list,
                                       'gy_MPU1': self.gy_MPU1_list, 'gz_MPU1': self.gz_MPU1_list,
                                       'ax_MPU2': self.ax_MPU2_list, 'ay_MPU2': self.ay_MPU2_list,
                                       'az_MPU2': self.az_MPU2_list, 'gx_MPU2': self.gx_MPU2_list,
                                       'gy_MPU2': self.gy_MPU2_list, 'gz_MPU2': self.gz_MPU2_list})
        elif 'MPU1_data' in self.table.columns:
            presave_df = pd.DataFrame({'SystemTime': self.table['SystemTime'],
                                       'ax_MPU1': self.ax_MPU1_list, 'ay_MPU1': self.ay_MPU1_list,
                                       'az_MPU1': self.az_MPU1_list, 'gx_MPU1': self.gx_MPU1_list,
                                       'gy_MPU1': self.gy_MPU1_list, 'gz_MPU1': self.gz_MPU1_list})
        else:
            print('Неизвестный формат таблицы')
            return

        if table_format == 'hdf':
            savename = file_name[0][:-3] + '_deciphered.h5'
            presave_df.to_hdf(file_name[0][:-3] + '_deciphered.h5', key='data', index=False)
        elif table_format == 'csv':
            savename = file_name[0][:-3] + '_deciphered.csv'
            presave_df.to_csv(file_name[0][:-3] + '_deciphered.csv', index=False)
        else:
            print('Неизвестный формат')
            return
        print('Таблица сохранена: ', savename)
