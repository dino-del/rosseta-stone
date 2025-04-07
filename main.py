import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from gui.main_window import MainWindow
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
