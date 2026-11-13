import io
import sys
from latex_tran import latex_tran
from flow_measure import flow_measure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

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


class ImageLabel(QLabel):
    """按标签大小等比缩放显示 QPixmap 的 QLabel。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._src: QPixmap | None = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_image(self, pm: QPixmap):
        self._src = pm
        self._rescale()

    def _rescale(self):
        if self._src is None or self._src.isNull():
            return
        self.setPixmap(self._src.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._rescale()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.measure = flow_measure()
        self._profile_cache: dict[int, QPixmap] = {}

        main_layout = QVBoxLayout()
        
        self.map_profile = ImageLabel()
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
        self.show_profile(idx)

    def show_profile(self, idx: int):
        pm = self._profile_cache.get(idx)
        if pm is None:
            pm = self._render_profile(idx)
            self._profile_cache[idx] = pm
        self.map_profile.set_image(pm)

    def _render_profile(self, idx: int) -> QPixmap:
        # 用独立的 Agg 画布渲染，避免 plot_profile 走 plt.show() 阻塞界面
        fig = Figure(figsize=(5.0, 4.6), dpi=120)
        FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)
        self.measure.plot_profile(
            self.measure.model_list[idx],
            title=f"Code: A{idx + 1}",
            ax=ax,
        )
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=200)
        pm = QPixmap()
        if not pm.loadFromData(buf.getvalue(), "PNG"):
            raise RuntimeError(f"Code: A{idx + 1} 云图渲染失败")
        return pm



app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()