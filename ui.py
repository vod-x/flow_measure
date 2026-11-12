import sys
from latex_tran import latex_tran
from flow_measure import flow_measure

from PySide6.QtCore import Qt

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
        self.measure = flow_measure()
        

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



        self.formula_raw = QLabel()
        self.label_raw = QLabel("原始模型：")
        self.label_raw.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.label_raw)
        self.formula_raw.setPixmap(latex_tran(r"(1-r)^{\frac{1}{n}}+mr(1-r)^{\frac{1}{k}}f(\theta)"))
        main_layout.addWidget(self.formula_raw)
        self.label_true = QLabel("实际模型：")
        self.label_true.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.label_true)
        self.formula_ture = QLabel("")
        main_layout.addWidget(self.formula_ture)


        self.select_formula = QComboBox()
        self.select_formula.addItems([f"Code: A{i}" for i in range(1, 15)])
        self.select_formula.currentIndexChanged.connect(self.change_formula)

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

        self.change_formula(0)

    def change_formula(self, idx: int):
        n, k, coefficient, f = self.measure.model_param_list[idx]
        formula = rf"(1-r)^{{\frac{{1}}{{{n}}}}}+{coefficient}r(1-r)^{{\frac{{1}}{{{k}}}}}{f}"
        self.formula_ture.setPixmap(latex_tran(formula))



app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()