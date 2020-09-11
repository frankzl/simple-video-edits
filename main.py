from code.main_widget import MainWidget
from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    
    app = QApplication([])
    app.setStyle("Fusion")

    window = MainWidget()

    window.show()
    app.exec_()
