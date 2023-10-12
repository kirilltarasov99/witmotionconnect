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

    def decipher(self):
        if 'MPU1_data' in self.table.columns:
            for i in range(len(self.table['MPU1_data'])):
                self.ax_MPU1_list.append(int.from_bytes(self.table['MPU1_data'][i][:2], byteorder='little', signed=True))
                self.ay_MPU1_list.append(int.from_bytes(self.table['MPU1_data'][i][2:4], byteorder='little', signed=True))
                self.az_MPU1_list.append(int.from_bytes(self.table['MPU1_data'][i][4:6], byteorder='little', signed=True))
                self.gx_MPU1_list.append(int.from_bytes(self.table['MPU1_data'][i][6:8], byteorder='little', signed=True))
                self.gy_MPU1_list.append(int.from_bytes(self.table['MPU1_data'][i][8:10], byteorder='little', signed=True))
                self.gz_MPU1_list.append(int.from_bytes(self.table['MPU1_data'][i][10:12], byteorder='little', signed=True))

        if 'MPU2_data' in self.table.columns:
            for i in range(len(self.table['MPU2_data'])):
                self.ax_MPU2_list.append(int.from_bytes(self.table['MPU2_data'][i][:2], byteorder='little', signed=True))
                self.ay_MPU2_list.append(int.from_bytes(self.table['MPU2_data'][i][2:4], byteorder='little', signed=True))
                self.az_MPU2_list.append(int.from_bytes(self.table['MPU2_data'][i][4:6], byteorder='little', signed=True))
                self.gx_MPU2_list.append(int.from_bytes(self.table['MPU2_data'][i][6:8], byteorder='little', signed=True))
                self.gy_MPU2_list.append(int.from_bytes(self.table['MPU2_data'][i][8:10], byteorder='little', signed=True))
                self.gz_MPU2_list.append(int.from_bytes(self.table['MPU2_data'][i][10:12], byteorder='little', signed=True))
        else:
            print('Unknown table format')
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
            print('Unknown table format')
            return

        if table_format == 'h5':
            savename = file_name[0][:-3] + '_deciphered.h5'
            presave_df.to_hdf(file_name[0][:-3] + '_deciphered.h5', key='data', index=False)
        elif table_format == 'csv':
            savename = file_name[0][:-3] + '_deciphered.csv'
            presave_df.to_csv(file_name[0][:-3] + '_deciphered.csv', index=False)
        else:
            print('Unknown format')
            return
        print('Table saved to: ', savename)
