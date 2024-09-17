class Settings(object):
    """
                :NOTE:
                    Class for settings widget.

                :args:
                    params_path (pathlib.Path): path to videocap params
                    view (QWidget): QT Widget object which is used for Settings window
    """

    def __init__(self, view, recorder_params_path, camera_params_path):
        self.vcap_params_path = recorder_params_path
        self._view = view

        with open(self.vcap_params_path, 'r') as file:
            self.params_recorder = file.readlines()

        self._view.VCap_address_lineEdit.setText(self.params_recorder[3].strip('\n'))
        self._view.VCap_record_resolution_lineEdit.setText(self.params_recorder[5].strip('\n'))
        self._view.VCap_FPS_lineEdit.setText(self.params_recorder[7].strip('\n'))
        self._view.VCap_stream_resolution_lineEdit.setText(self.params_recorder[9].strip('\n'))

        with open(camera_params_path, 'r') as file:
            self.params_camera = file.readlines()

        self._view.Camera_address_lineEdit.setText(self.params_camera[3].strip('\n'))
        self._view.Camera_record_resolution_lineEdit.setText(self.params_camera[5].strip('\n'))
        self._view.Camera_FPS_lineEdit.setText(self.params_camera[7].strip('\n'))
        self._view.Camera_stream_resolution_lineEdit.setText(self.params_camera[9].strip('\n'))
        
        if self.params_recorder[1].strip("\n") == '1':
            self.use_recorder = True
        else:
            self.use_recorder = False

        if self.params_camera[1].strip("\n") == '1':
            self.use_camera = True
        else:
            self.use_camera = False
        
        if self.use_recorder:
            self._view.VCap_use_checkBox.setChecked(1)

        if self.use_camera:
            self._view.Camera_use_checkBox.setChecked(1)

    def save(self):
        """
                :NOTE:
                    Saves settings into a text file.
        """

        if self._view.VCap_use_checkBox.isChecked():
            self.params_recorder[1] = '1\n'
        else:
            self.params_recorder[1] = '0\n'

        self.params_recorder[3] = str(self._view.VCap_address_lineEdit.text() + '\n')
        self.params_recorder[5] = str(self._view.VCap_record_resolution_lineEdit.text() + '\n')
        self.params_recorder[7] = str(self._view.VCap_FPS_lineEdit.text() + '\n')
        self.params_recorder[9] = str(self._view.VCap_stream_resolution_lineEdit.text() + '\n')

        with open(self.vcap_params_path, 'w') as file:
            file.writelines(self.params_recorder)

        if self._view.Camera_use_checkBox.isChecked():
            self.params_camera[1] = '1\n'
        else:
            self.params_camera[1] = '0\n'
        
        self.params_camera[3] = str(self._view.Camera_address_lineEdit.text() + '\n')
        self.params_camera[5] = str(self._view.Camera_resolution_lineEdit.text() + '\n')
        self.params_camera[7] = str(self._view.Camera_FPS_lineEdit.text() + '\n')
        self.params_camera[9] = str(self._view.Camera_stream_resolution_lineEdit.text() + '\n')
                            
        with open(self.camera_params_path, 'w') as file:
            file.writelines(self.params_camera)
