import sys
from latex_tran import latex_tran
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QSizePolicy,
    QDial,
)
from PySide6.QtGui import(
    QPixmap,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        main_layout = QVBoxLayout()
        
        self.map_profile = QLabel("test")
        self.map_axis = QLabel("test")
        for map_widget in (self.map_profile, self.map_axis):
            map_widget.setMinimumSize(200, 200)
            map_widget.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding,
            )
        map_layout = QHBoxLayout()
        map_layout.addWidget(self.map_profile, 1)
        map_layout.addWidget(self.map_axis, 1)

        main_layout.addLayout(map_layout, 1)



        self.formula_raw = QLabel("test")
        main_layout.addWidget(self.formula_raw)
        self.formula_ture = QLabel("test")
        main_layout.addWidget(self.formula_ture)

        self.select_formula = QComboBox()
        self.select_model = QComboBox()
        select_layout = QHBoxLayout()
        select_layout.addWidget(self.select_formula)
        select_layout.addWidget(self.select_model)

        main_layout.addLayout(select_layout)

        self.dial = QDial()
        main_layout.addWidget(self.dial)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()