import pandas as pd
from pathlib import Path


class Decipher(object):
    """
                :NOTE:
                    Class for Decipher function of the app.

                :args:
                    QToutput (QTextEdit): GUI object for output messages
            """

    def __init__(self, QToutput):
        self.output = QToutput
        self.table = pd.DataFrame
        self.ax_MPU1_list = []
        self.ay_MPU1_list = []
        self.az_MPU1_list = []
        self.gx_MPU1_list = []
        self.gy_MPU1_list = []
        self.gz_MPU1_list = []
        self.mx_MPU1_list = []
        self.my_MPU1_list = []
        self.mz_MPU1_list = []
        self.ax_MPU2_list = []
        self.ay_MPU2_list = []
        self.az_MPU2_list = []
        self.gx_MPU2_list = []
        self.gy_MPU2_list = []
        self.gz_MPU2_list = []
        self.mx_MPU2_list = []
        self.my_MPU2_list = []
        self.mz_MPU2_list = []

        self.magBias_MPU1 = [30, 270, -100]
        self.magBias_MPU2 = [30, 270, -100]
        self.magCalibration = [1.16, 1.16, 1.21]
        self.mRes = 10. * 1229. / 4096.

    def open(self, file_name):
        """
                    :NOTE:
                        Opens hdf table containing raw sensor values.

                    :args:
                        file_name (string): path to file
                """

        self.table = pd.read_hdf(file_name[0], key='data')

    def decipher(self, acc_range, gyro_range, params_path):
        """
                    :NOTE:
                        Converts hdf table containing raw sensor values to readable format.
                        Constant values for conversion:
                        https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-9150-Datasheet.pdf
                        (from p. 11, Sensitivity Scale Factor)

                    :args:
                        acc_range (string): accelerometer sensitivity
                        gyro_range (string): gyroscope sensitivity
                        params_path (pathlib.Path): path of magnetometer calibration file
                """

        self.output.append('Дешифрование...')
        with open(params_path, 'r') as file:
            lines = file.readlines()
        if 'MPU1_data' in self.table.columns:
            if len(lines[2]) > 2:
                self.magBias_MPU1 = [float(i)*10 for i in lines[2].strip("\n").split('     ')]

            for i in range(len(self.table['MPU1_data'])):
                ax = int.from_bytes(self.table['MPU1_data'][i][:2], byteorder='big', signed=True)
                ay = int.from_bytes(self.table['MPU1_data'][i][2:4], byteorder='big', signed=True)
                az = int.from_bytes(self.table['MPU1_data'][i][4:6], byteorder='big', signed=True)
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

                gx = int.from_bytes(self.table['MPU1_data'][i][6:8], byteorder='big', signed=True)
                gy = int.from_bytes(self.table['MPU1_data'][i][8:10], byteorder='big', signed=True)
                gz = int.from_bytes(self.table['MPU1_data'][i][10:12], byteorder='big', signed=True)
                if gyro_range == '250 deg/s':
                    gx /= 131
                    gy /= 131
                    gz /= 131
                elif gyro_range == '500 deg/s':
                    gx /= 65.5
                    gy /= 65.5
                    gz /= 65.5
                elif gyro_range == '1000 deg/s':
                    gx /= 32.8
                    gy /= 32.8
                    gz /= 32.8
                elif gyro_range == '2000 deg/s':
                    gx /= 16.4
                    gy /= 16.4
                    gz /= 16.4

                self.gx_MPU1_list.append(gx)
                self.gy_MPU1_list.append(gy)
                self.gz_MPU1_list.append(gz)

                if len(self.table['MPU1_data'][i]) == 18:
                    mx = int.from_bytes(self.table['MPU1_data'][i][12:14], byteorder='little', signed=True)
                    my = int.from_bytes(self.table['MPU1_data'][i][14:16], byteorder='little', signed=True)
                    mz = int.from_bytes(self.table['MPU1_data'][i][16:18], byteorder='little', signed=True)

                    mx = mx * self.mRes * self.magCalibration[0] - self.magBias_MPU1[0]
                    my = my * self.mRes * self.magCalibration[1] - self.magBias_MPU1[1]
                    mz = mz * self.mRes * self.magCalibration[2] - self.magBias_MPU1[2]

                else:
                    mx = 0
                    my = 0
                    mz = 0

                self.mx_MPU1_list.append(mx)
                self.my_MPU1_list.append(my)
                self.mz_MPU1_list.append(mz)

        if 'MPU2_data' in self.table.columns:
            if len(lines[5]) > 2:
                self.magBias_MPU2 = [float(i) * 10 for i in lines[5].strip("\n").split('     ')]
            for i in range(len(self.table['MPU2_data'])):
                ax = int.from_bytes(self.table['MPU2_data'][i][:2], byteorder='big', signed=True)
                ay = int.from_bytes(self.table['MPU2_data'][i][2:4], byteorder='big', signed=True)
                az = int.from_bytes(self.table['MPU2_data'][i][4:6], byteorder='big', signed=True)
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

                gx = int.from_bytes(self.table['MPU2_data'][i][6:8], byteorder='big', signed=True)
                gy = int.from_bytes(self.table['MPU2_data'][i][8:10], byteorder='big', signed=True)
                gz = int.from_bytes(self.table['MPU2_data'][i][10:12], byteorder='big', signed=True)
                if gyro_range == '250 deg/s':
                    gx /= 131
                    gy /= 131
                    gz /= 131
                elif gyro_range == '500 deg/s':
                    gx /= 65.5
                    gy /= 65.5
                    gz /= 65.5
                elif gyro_range == '1000 deg/s':
                    gx /= 32.8
                    gy /= 32.8
                    gz /= 32.8
                elif gyro_range == '2000 deg/s':
                    gx /= 16.4
                    gy /= 16.4
                    gz /= 16.4

                self.gx_MPU2_list.append(gx)
                self.gy_MPU2_list.append(gy)
                self.gz_MPU2_list.append(gz)

                if len(self.table['MPU2_data'][i]) == 18:
                    mx = int.from_bytes(self.table['MPU2_data'][i][12:14], byteorder='little', signed=True)
                    my = int.from_bytes(self.table['MPU2_data'][i][14:16], byteorder='little', signed=True)
                    mz = int.from_bytes(self.table['MPU2_data'][i][16:18], byteorder='little', signed=True)

                    mx = mx * self.mRes * self.magCalibration[0] - self.magBias_MPU2[0]
                    my = my * self.mRes * self.magCalibration[1] - self.magBias_MPU2[1]
                    mz = mz * self.mRes * self.magCalibration[2] - self.magBias_MPU2[2]
                else:
                    mx = 0
                    my = 0
                    mz = 0

                self.mx_MPU2_list.append(mx)
                self.my_MPU2_list.append(my)
                self.mz_MPU2_list.append(mz)

        else:
            self.output.append('Неизвестный формат таблицы')
            return

    def save(self, file_name, path, table_format):
        """
                    :NOTE:
                        Saves converted table into chosen format.

                    :args:
                        file_name (string): name of source table
                        path (pathlib.Path): path to data folder
                        table_format (string): chosen save format
                """

        if 'MPU2_data' in self.table.columns:
            presave_df = pd.DataFrame({'SystemTime': self.table['SystemTime'],
                                       'ax_MPU1': self.ax_MPU1_list, 'ay_MPU1': self.ay_MPU1_list, 'az_MPU1': self.az_MPU1_list,
                                       'gx_MPU1': self.gx_MPU1_list, 'gy_MPU1': self.gy_MPU1_list, 'gz_MPU1': self.gz_MPU1_list,
                                       'mx_MPU1': self.mx_MPU1_list, 'my_MPU1': self.my_MPU1_list, 'mz_MPU1': self.mz_MPU1_list,
                                       'ax_MPU2': self.ax_MPU2_list, 'ay_MPU2': self.ay_MPU2_list, 'az_MPU2': self.az_MPU2_list,
                                       'gx_MPU2': self.gx_MPU2_list, 'gy_MPU2': self.gy_MPU2_list, 'gz_MPU2': self.gz_MPU2_list,
                                       'mx_MPU2': self.mx_MPU2_list, 'my_MPU2': self.my_MPU2_list, 'mz_MPU2': self.mz_MPU2_list})

        elif 'MPU1_data' in self.table.columns:
            presave_df = pd.DataFrame({'SystemTime': self.table['SystemTime'],
                                       'ax_MPU1': self.ax_MPU1_list, 'ay_MPU1': self.ay_MPU1_list, 'az_MPU1': self.az_MPU1_list,
                                       'gx_MPU1': self.gx_MPU1_list, 'gy_MPU1': self.gy_MPU1_list, 'gz_MPU1': self.gz_MPU1_list,
                                       'mx_MPU1': self.mx_MPU1_list, 'my_MPU1': self.my_MPU1_list, 'mz_MPU1': self.mz_MPU1_list})

        else:
            self.output.append('Неизвестный формат таблицы')
            self.clean_lists()
            return

        self.clean_lists()
        if table_format == 'hdf':
            savename = Path(path, file_name[0][-25:-3] + '_deciphered.h5')
            presave_df.to_hdf(savename, key='data', index=False)
        elif table_format == 'csv':
            savename = Path(path, file_name[0][-25:-3] + '_deciphered.csv')
            presave_df.to_csv(savename, index=False)
        else:
            self.output.append('Неизвестный формат')
            return

        self.output.append('Таблица сохранена: ' + str(savename))

    def clean_lists(self):
        self.ax_MPU1_list = []
        self.ay_MPU1_list = []
        self.az_MPU1_list = []
        self.gx_MPU1_list = []
        self.gy_MPU1_list = []
        self.gz_MPU1_list = []
        self.mx_MPU1_list = []
        self.my_MPU1_list = []
        self.mz_MPU1_list = []
        self.ax_MPU2_list = []
        self.ay_MPU2_list = []
        self.az_MPU2_list = []
        self.gx_MPU2_list = []
        self.gy_MPU2_list = []
        self.gz_MPU2_list = []
        self.mx_MPU2_list = []
        self.my_MPU2_list = []
        self.mz_MPU2_list = []
