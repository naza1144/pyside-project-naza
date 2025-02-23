import sys
from PySide6 import QtWidgets

app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QWidget()
window.resize(400, 500) 
window.setWindowTitle("PySide6")
window.show()
sys.exit(app.exec())