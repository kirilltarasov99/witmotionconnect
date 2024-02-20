class Settings(object):
    """
                :NOTE:
                    Class for settings widget.

                :args:
                    params_path (pathlib.Path): path to videocap params
                    view (QWidget): QT Widget object which is used for Settings window
    """

    def __init__(self, params_path, view):
        self.vcap_params_path = params_path
        self._view = view

        with open(self.vcap_params_path, 'r') as file:
            self.params = file.readlines()

        self._view.VCap_FPS_lineEdit.setText(self.params[7].strip('\n'))
        self._view.VCap_resolution_lineEdit.setText(self.params[5].strip('\n'))
        self._view.VCap_address_lineEdit.setText(self.params[3].strip('\n'))

        if self.params[1].strip("\n") == '1':
            self.use = True
        else:
            self.use = False

        if self.use:
            self._view.VCap_use_checkBox.setChecked(1)

    def save(self):
        """
                :NOTE:
                    Saves settings into a text file.
        """

        if self._view.VCap_use_checkBox.isChecked():
            self.params[1] = '1\n'
        else:
            self.params[1] = '0\n'

        self.params[3] = str(self._view.VCap_address_lineEdit.text() + '\n')
        self.params[5] = str(self._view.VCap_resolution_lineEdit.text() + '\n')
        self.params[7] = str(self._view.VCap_FPS_lineEdit.text() + '\n')

        with open(self.vcap_params_path, 'w') as file:
            file.writelines(self.params)
