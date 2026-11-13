import io
import math
import sys

import numpy as np
import matplotlib as mpl

# matplotlib 默认字体没有中文字形, 不设置的话坐标轴标签会显示成方框
mpl.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun",
                                   "Noto Sans CJK SC", "DejaVu Sans"]
mpl.rcParams["axes.unicode_minus"] = False
from typing import Callable
from latex_tran import latex_tran
from flow_measure import flow_measure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from PySide6.QtCore import Qt, QPointF

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
    QColor,
    QPainter,
    QPen,
    QPixmap,
    QTransform,
)


# 四条声线到圆心的距离（单位圆半径 = 1），按 ±0.80、±0.30 排布
PATH_DISTANCES = (-0.80, -0.30, 0.30, 0.80)
# dial 满量程对应的旋转角度（度）
DIAL_ANGLE_SPAN = 180.0


def data_to_image(ax, fig) -> QTransform:
    """建立数据坐标（单位圆）到 PNG 像素坐标的仿射映射。"""
    height = fig.get_figheight() * fig.dpi

    def to_image(x: float, y: float) -> QPointF:
        px, py = ax.transData.transform((x, y))
        return QPointF(px, height - py)          # 图像坐标 y 轴朝下

    o = to_image(0.0, 0.0)
    ex = to_image(1.0, 0.0)
    ey = to_image(0.0, 1.0)
    return QTransform(
        ex.x() - o.x(), ex.y() - o.y(),
        ey.x() - o.x(), ey.y() - o.y(),
        o.x(), o.y(),
    )


class ImageLabel(QLabel):
    """按标签大小等比缩放显示 QPixmap 的 QLabel，可在图上叠加矢量元素。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._src: QPixmap | None = None
        self._data_to_image: QTransform | None = None
        self._overlay: Callable[[QPainter, Callable[[float, float], QPointF]], None] | None = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_image(self, pm: QPixmap, data_to_image: QTransform | None = None):
        self._src = pm
        self._data_to_image = data_to_image
        self._rescale()

    def set_overlay(self, drawer):
        """drawer(painter, to_widget)：按数据坐标绘制，to_widget(x, y) 返回控件坐标。"""
        self._overlay = drawer
        self.update()

    def _rescale(self):
        if self._src is None or self._src.isNull():
            return
        self.setPixmap(self._src.scaled(
            self.contentsRect().size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._rescale()

    def paintEvent(self, event):
        super().paintEvent(event)
        pm = self.pixmap()
        if self._overlay is None or self._data_to_image is None or pm is None or pm.isNull():
            return
        rect = self.contentsRect()
        k = pm.width() / self._src.width()
        ox = rect.x() + (rect.width() - pm.width()) / 2
        oy = rect.y() + (rect.height() - pm.height()) / 2

        def to_widget(x: float, y: float) -> QPointF:
            p = self._data_to_image.map(QPointF(x, y))
            return QPointF(ox + p.x() * k, oy + p.y() * k)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._overlay(painter, to_widget)
        painter.end()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.measure = flow_measure()
        self._profile_cache: dict[int, QPixmap] = {}
        self._qref_cache: dict[int, float] = {}
        self._curve_cache: dict[tuple, tuple] = {}
        self.path_angle_deg = 0.0
        self._curve_xlim = (0.0, 180.0)
        self._curve_ylim = (-1.0, 1.0)
        self._curve_angles = None
        self._curve_eps = None

        main_layout = QVBoxLayout()
        
        self.map_profile = ImageLabel()
        self.map_axis = ImageLabel()
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
        self.select_model.addItems(list(self.measure.SCHEMES))
        self.select_model.currentTextChanged.connect(lambda _: self.show_error_curve())
        select_layout = QHBoxLayout()
        select_layout.addWidget(self.select_formula)
        select_layout.addWidget(self.select_model)

        main_layout.addLayout(select_layout)

        self.dial = QDial()
        self.dial.setRange(0, 180)
        self.dial.valueChanged.connect(self.rotate_paths)
        main_layout.addWidget(self.dial)

        self.readout = QLabel("")
        self.readout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.readout)

        self.path_angle_deg = 0.0
        self.map_profile.set_overlay(self.draw_acoustic_paths)
        self.map_axis.set_overlay(self.draw_angle_marker)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.change_formula(0)

    def change_formula(self, idx: int):
        n, k, coefficient, f = self.measure.model_param_list[idx]
        formula = rf"(1-r)^{{\frac{{1}}{{{n}}}}}+{coefficient}r(1-r)^{{\frac{{1}}{{{k}}}}}{f}"
        self.formula_ture.setPixmap(latex_tran(formula))
        self.show_profile(idx)
        self.show_error_curve()

    def show_profile(self, idx: int):
        entry = self._profile_cache.get(idx)
        if entry is None:
            entry = self._render_profile(idx)
            self._profile_cache[idx] = entry
        pm, transform = entry
        self.map_profile.set_image(pm, transform)

    def _render_profile(self, idx: int) -> tuple[QPixmap, QTransform]:
        # 用独立的 Agg 画布渲染，避免 plot_profile 走 plt.show() 阻塞界面
        fig = Figure(figsize=(5.0, 4.6), dpi=200)
        FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)
        self.measure.plot_profile(
            self.measure.model_list[idx],
            title=f"Code: A{idx + 1}",
            ax=ax,
        )
        fig.canvas.draw()                       # 先完成布局，transData 才是最终位置
        transform = data_to_image(ax, fig)
        buf = io.BytesIO()
        # 不能用 bbox_inches="tight"，否则图像会被裁剪、与 transform 失配
        fig.savefig(buf, format="png")
        pm = QPixmap()
        if not pm.loadFromData(buf.getvalue(), "PNG"):
            raise RuntimeError(f"Code: A{idx + 1} 云图渲染失败")
        return pm, transform

    def rotate_paths(self, value: int):
        self.path_angle_deg = value / self.dial.maximum() * DIAL_ANGLE_SPAN
        self.map_profile.update()
        self.map_axis.update()
        self.update_readout()


    # ---------------- 误差-角度曲线 ----------------
    def current_scheme(self) -> str:
        combo = getattr(self, "select_model", None)
        text = combo.currentText() if combo is not None else ""
        return text if text in self.measure.SCHEMES else "Gauss-Jacobi"

    def show_error_curve(self):
        """按当前模型与积分方法渲染 ε(α) 曲线, 并显示到 self.map_axis。"""
        idx = self.select_formula.currentIndex()
        scheme = self.current_scheme()
        key = (idx, scheme)
        entry = self._curve_cache.get(key)
        if entry is None:
            entry = self._render_error_curve(idx, scheme)
            self._curve_cache[key] = entry
        pm, transform, xlim, ylim, angles, eps = entry
        self._curve_xlim, self._curve_ylim = xlim, ylim
        self._curve_angles, self._curve_eps = angles, eps
        self.map_axis.set_image(pm, transform)
        self.map_axis.update()
        self.update_readout()

    def _render_error_curve(self, idx: int, scheme: str):
        profile = self.measure.model_list[idx]
        q_ref = self._qref_cache.get(idx)
        if q_ref is None:
            q_ref = self.measure.reference_flow(profile, Nw=401, Nt=360)
            self._qref_cache[idx] = q_ref
        angles, eps = self.measure.error_curve(profile, scheme, q_ref=q_ref)

        fig = Figure(figsize=(5.0, 4.6), dpi=200)
        FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)
        ax.plot(angles, eps, "-", lw=1.4, color="#2b6cb0")
        ax.axhline(0.0, color="0.4", lw=0.8, ls="--")
        ax.set_xlim(0.0, 180.0)
        span = max(0.05, float(np.max(np.abs(eps))) * 1.2)
        ax.set_ylim(-span, span)
        ax.set_xticks(np.arange(0, 181, 30))
        ax.set_xlabel("旋转角 α (°)")
        ax.set_ylabel("测量误差 ε (%)")
        ax.set_title("%s    Code: A%d" % (scheme, idx + 1), fontsize=10)
        ax.grid(alpha=0.3)

        fig.canvas.draw()                       # 先完成布局, transData 才是最终位置
        transform = data_to_image(ax, fig)
        buf = io.BytesIO()
        fig.savefig(buf, format="png")          # 不能用 bbox_inches="tight"
        pm = QPixmap()
        if not pm.loadFromData(buf.getvalue(), "PNG"):
            raise RuntimeError("Code: A%d 误差曲线渲染失败" % (idx + 1))
        return pm, transform, (0.0, 180.0), (-span, span), angles, eps

    def update_readout(self):
        """当前角度与对应误差的读数(用 QLabel 显示)。"""
        if not hasattr(self, "readout"):
            return
        text = "α = %.0f°" % self.path_angle_deg
        if self._curve_eps is not None and self._curve_eps.size:
            value = float(np.interp(self.path_angle_deg,
                                    self._curve_angles, self._curve_eps))
            text += "    ε = %+.3f%%" % value
        text += "    (%s, Code: A%d)" % (self.current_scheme(),
                                       self.select_formula.currentIndex() + 1)
        self.readout.setText(text)

    def draw_angle_marker(self, painter: QPainter, to_widget):
        """在误差曲线图上叠加当前旋转角的竖线与读数(实时, 不重算曲线)。"""
        x = self.path_angle_deg
        y0, y1 = self._curve_ylim
        painter.setPen(QPen(QColor(220, 38, 38), 1.8, Qt.PenStyle.DashLine))
        painter.drawLine(to_widget(x, y0), to_widget(x, y1))

    def draw_acoustic_paths(self, painter: QPainter, to_widget):
        """在云图上叠加四条平行声线，方向由 dial 控制。"""
        a = math.radians(self.path_angle_deg)
        ux, uy = math.cos(a), math.sin(a)        # 声线方向
        nx, ny = -uy, ux                          # 法向，用于偏移距离
        halo = QPen(QColor(255, 255, 255, 210), 3.4, Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.FlatCap)
        core = QPen(QColor(25, 25, 25), 1.4, Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.FlatCap)
        for d in PATH_DISTANCES:
            half = math.sqrt(1.0 - d * d)
            p1 = to_widget(d * nx - half * ux, d * ny - half * uy)
            p2 = to_widget(d * nx + half * ux, d * ny + half * uy)
            painter.setPen(halo)
            painter.drawLine(p1, p2)
            painter.setPen(core)
            painter.drawLine(p1, p2)



app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()