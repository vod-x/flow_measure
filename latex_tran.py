import io
from matplotlib import mathtext, rc_context
from matplotlib.font_manager import FontProperties

from PySide6.QtGui import QPixmap

_cache: dict[tuple, QPixmap] = {}
def latex_tran(tex: str, pt: int = 24, color: str = "#FFAE00", dpr: float = 2.0) -> QPixmap:
    key = (tex, pt, color, dpr)
    if key in _cache:
        return _cache[key]

    buf = io.BytesIO()
    with rc_context({"savefig.transparent": True}):
        mathtext.math_to_image(
            f"${tex}$", buf,
            prop=FontProperties(size=pt),
            dpi=72 * dpr,          # 关键：按 2 倍分辨率渲染
            format="png",
            color=color,
        )
    pm = QPixmap()
    pm.loadFromData(buf.getvalue(), "PNG")
    pm.setDevicePixelRatio(dpr)  # 逻辑尺寸回到 pt
    _cache[key] = pm
    return pm