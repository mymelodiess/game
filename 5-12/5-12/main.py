# main.py
import sys
from PyQt5.QtWidgets import QApplication
from ui import SudokuApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SudokuApp()
    ex.showFullScreen()  
    sys.exit(app.exec_())