from PyQt5 import QtWidgets
import sys
from GUI.window import Ui_Form

if __name__ =='__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(widget)
    widget.show()
    sys.exit(app.exec_())