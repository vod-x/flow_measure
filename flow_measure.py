from numpy import cos, exp, pi, sin
import numpy as np
import matplotlib.pyplot as plt
from types import SimpleNamespace

class flow_measure():
    def __init__(self):
        self.model_param_list = [
        (9, 4,   r"-\frac{0.5}{\pi}",          r"\theta\sin\theta"),                          # A1
        (7, 9,   r"-\frac{0.4}{\pi}",          r"\theta\sin\theta"),                          # A2
        (9, 4,   r"\frac{0.04}{\pi}",          r"(\theta^{2}-1)(1-\cos\theta)^{2}"),          # A3
        (9, 0.5, r"3.3170",                    r"e^{-0.5\theta}\sin\theta"),                  # A4  (a=0.5)
        (7, 9,   r"\frac{e^{0.1\pi}}{2}",      r"e^{-0.2\theta}\sin\theta"),                  # A5  (a=0.2)
        (7, 9,   r"-\frac{e^{0.1\pi}}{2}",     r"e^{-0.2\theta}\sin\theta"),                  # A6  (a=0.2)
        (9, 4,   r"\frac{2}{\pi^{5}}",         r"\theta^{2}(2\pi-\theta)^{2}"),               # A7
        (9, 4,   r"\frac{1}{\pi^{2}}",         r"\theta\,(1-\cos^{2}\theta)"),                # A8
        (9, 4,   r"\frac{2}{\pi^{3}}",         r"\theta\,(2\pi-\theta)\sin^{2}\theta"),       # A9
        (9, 9,   r"0.6813",                    r"e^{-0.1\theta}\sin^{2}\theta"),              # A10 (a=0.1)
        (7, 9,   r"e^{0.1\pi}",                r"e^{-0.2\theta}\sin^{2}\theta"),              # A11 (a=0.2)
        (9, 0.5, r"-6.7501",                   r"e^{-0.5\theta}\sin\theta"),                  # A12 (a=0.5)
        (7, 9,   r"\frac{1}{2\pi^{2}}",        r"(2\pi-\theta)^{2}\,\theta\,\sin 3\theta"),   # A13
        (4, 9,   r"\frac{e^{0.15\pi}}{2}",     r"e^{-0.3\theta}\sin^{2}5\theta"),             # A14 (a=0.3)
        ]

        self.model_list = [
                lambda self: (1 - self.r)**(1/9)
                 - (0.5/pi) * self.r * (1 - self.r)**(1/4) * self.theta * sin(self.theta),

                # A2:  n=7,  k=9,   m=-0.4/π
                lambda self: (1 - self.r)**(1/7)
                             - (0.4/pi) * self.r * (1 - self.r)**(1/9) * self.theta * sin(self.theta),

                # A3:  n=9,  k=4,   m=0.04/π,                     f=(θ²-1)(1-cosθ)²
                lambda self: (1 - self.r)**(1/9)
                             + (0.04/pi) * self.r * (1 - self.r)**(1/4)
                             * (self.theta**2 - 1) * (1 - cos(self.theta))**2,

                # A4:  n=9,  k=0.5, m=3.3170,   a=0.5   → (1-r)^(1/0.5)=(1-r)^2
                lambda self: (1 - self.r)**(1/9)
                             + 3.3170 * self.r * (1 - self.r)**2
                             * exp(-0.5 * self.theta) * sin(self.theta),

                # A5:  n=7,  k=9,   m=e^(0.1π)/2, a=0.2
                lambda self: (1 - self.r)**(1/7)
                             + (exp(0.1*pi) / 2) * self.r * (1 - self.r)**(1/9)
                             * exp(-0.2 * self.theta) * sin(self.theta),

                # A6:  n=7,  k=9,   m=-e^(0.1π)/2, a=0.2
                lambda self: (1 - self.r)**(1/7)
                             - (exp(0.1*pi) / 2) * self.r * (1 - self.r)**(1/9)
                             * exp(-0.2 * self.theta) * sin(self.theta),

                # A7:  n=9,  k=4,   m=2/π⁵,                       f=θ²(2π-θ)²
                lambda self: (1 - self.r)**(1/9)
                             + (2 / pi**5) * self.r * (1 - self.r)**(1/4)
                             * self.theta**2 * (2*pi - self.theta)**2,

                # A8:  n=9,  k=4,   m=1/π²,                       f=θ(1-cos²θ)
                lambda self: (1 - self.r)**(1/9)
                             + (1 / pi**2) * self.r * (1 - self.r)**(1/4)
                             * self.theta * (1 - cos(self.theta)**2),

                # A9:  n=9,  k=4,   m=2/π³,                       f=θ(2π-θ)sin²θ
                lambda self: (1 - self.r)**(1/9)
                             + (2 / pi**3) * self.r * (1 - self.r)**(1/4)
                             * self.theta * (2*pi - self.theta) * sin(self.theta)**2,

                # A10: n=9,  k=9,   m=0.6813,   a=0.1
                lambda self: (1 - self.r)**(1/9)
                             + 0.6813 * self.r * (1 - self.r)**(1/9)
                             * exp(-0.1 * self.theta) * sin(self.theta)**2,

                # A11: n=7,  k=9,   m=e^(0.1π), a=0.2
                lambda self: (1 - self.r)**(1/7)
                             + exp(0.1*pi) * self.r * (1 - self.r)**(1/9)
                             * exp(-0.2 * self.theta) * sin(self.theta)**2,

                # A12: n=9,  k=0.5, m=-6.7501,  a=0.5
                lambda self: (1 - self.r)**(1/9)
                             - 6.7501 * self.r * (1 - self.r)**2
                             * exp(-0.5 * self.theta) * sin(self.theta),

                # A13: n=7,  k=9,   m=1/(2π²),                    f=(2π-θ)²θsin3θ
                lambda self: (1 - self.r)**(1/7)
                             + (1 / (2*pi**2)) * self.r * (1 - self.r)**(1/9)
                             * (2*pi - self.theta)**2 * self.theta * sin(3*self.theta),

                # A14: n=4,  k=9,   m=e^(0.15π)/2, a=0.3
                lambda self: (1 - self.r)**(1/4)
                             + (exp(0.15*pi) / 2) * self.r * (1 - self.r)**(1/9)
                             * exp(-0.3 * self.theta) * sin(5 * self.theta)**2,

        ]
    def plot_profile(self,profile, title=None, N=401, n_levels=10, cmap="jet",
                save=None, ax=None, colorbar=True, contour_lines=True):
        """
        输入: profile —— PROFILES 数组中的某个成员(形如 lambda self: ...)
        输出: 一张彩色云图, 颜色 = v / v_max ∈ [0, 1]; 管壁处 0, 最热点 1

        参数
        ----
        N              : 网格分辨率(每边点数), 401 已足够平滑
        n_levels       : 色阶数(等值填色条数), 样图约 6~10
        save           : 若给文件名则存图(如 "A1.png")
        ax             : 传入已有坐标系则画在上面, 便于批量排版
        """
        # 1) 单位圆网格 (r, θ)
        g = np.linspace(-1.0, 1.0, N)
        X, Z = np.meshgrid(g, g)
        R = np.hypot(X, Z)
        T = np.mod(np.arctan2(Z, X), 2 * np.pi)          # 必须 [0, 2π)

        # 2) 组装 self, 调用剖面函数
        prof = SimpleNamespace(r=R, theta=T, alpha=T)     # alpha 是 theta 的别名, 防止属性名不一致
        V = np.asarray(profile(prof), dtype=float)

        # 3) 圆外裁掉 + 按自身最大值归一化
        V = np.ma.masked_where(R > 1.0, V)
        vmax = float(V.max())
        if vmax <= 0:
            raise ValueError("v_max <= 0, 无法归一化")
        Vn = np.clip(V / vmax, 0.0, 1.0)                  # (0, 1]

        # 4) 画图
        own = ax is None
        if own:
            fig, ax = plt.subplots(figsize=(5.0, 4.6), dpi=120)
        else:
            fig = ax.figure

        cf = ax.contourf(X, Z, Vn, levels=n_levels, cmap=cmap,
                        vmin=0.0, vmax=1.0, extend="neither")
        if contour_lines:
            ax.contour(X, Z, Vn, levels=n_levels, colors="k", linewidths=0.8)
        if colorbar:
            fig.colorbar(cf, ax=ax, fraction=0.046, pad=0.02)

        ax.set_aspect("equal")
        ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)
        ax.set_xticks(np.arange(-1, 1.01, 0.5))
        ax.set_yticks(np.arange(-1, 1.01, 0.5))
        ax.tick_params(labelsize=8)
        if title:
            ax.set_title(title, fontsize=10)
        if save:
            fig.savefig(save, bbox_inches="tight", dpi=200)
        if own:
            plt.show()
        return fig

