# main.py

import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import OperationsCommandCenter

def main():
    app = QApplication(sys.argv)
    window = OperationsCommandCenter()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
