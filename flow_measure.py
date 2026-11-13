from numpy import cos, exp, pi, sin
import numpy as np
import matplotlib.pyplot as plt
from types import SimpleNamespace
from collections import namedtuple

# numpy>=2.0 移除了 np.trapz, 统一用 trapezoid; 旧版本回退到 trapz
_trapz = getattr(np, "trapezoid", None) or getattr(np, "trapz")

# chord_flow() 的返回值: 具名元组, 可按名字或下标取值
ChordResult = namedtuple(
    "ChordResult",
    "v_bar chord_length line_integral flow_per_dz flow omega_contrib max_v d theta_deg")


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

    # ---------------------------------------------------------------
    # 四声道积分方案: (声道相对高度 d, 权系数 ω)
    # ---------------------------------------------------------------
    SCHEMES = {
        "Gauss-Jacobi": [(0.309017, 0.597566), (0.809017, 0.369316)],
        "OWCIS": [(0.303783, 0.588228), (0.799639, 0.371884)],
    }

    def chord_flow(self, profile, d, theta_deg, N=401, R=1.0, vc=1.0,
                   dz=None, omega=None, degrees=True):
        """沿一条声道计算该流型的速度与流量。

        profile   : model_list 中的某个成员 (lambda self: ...)
        d         : 声道到圆心的距离, 以半径为单位, 要求 |d| < 1
        theta_deg : 声道方位角(度, 自 +x 轴逆时针); degrees=False 时按弧度传入
        N         : 沿弦采样点数(余弦聚集, 401 点精度约 1e-5)
        R, vc     : 物理半径[m] 与管心速度[m/s]; 默认 1,1 得到归一化结果
        dz        : 若给定, 顺带算出该窄条的体积流量[m^3/s]
        omega     : 若给定该声道权系数, 顺带算出它在总流量中的份额

        返回 ChordResult(v_bar, chord_length, line_integral, flow_per_dz,
                         flow, omega_contrib, max_v, d, theta_deg)
        """
        th = float(theta_deg) if not degrees else np.deg2rad(theta_deg)
        d = float(d)
        if not (-1.0 < d < 1.0):
            raise ValueError("|d| 必须小于 1: 声道不能落在管壁上")

        c_n = 2.0 * np.sqrt(1.0 - d * d)                      # 归一化弦长
        nv = (-sin(th), cos(th))                              # 弦的法向
        ev = (cos(th), sin(th))                               # 弦的切向
        s_n = (c_n / 2.0) * np.cos(np.linspace(pi, 0.0, N))    # 端点加密的采样点

        x_n = d * nv[0] + s_n * ev[0]
        z_n = d * nv[1] + s_n * ev[1]
        r = np.clip(np.hypot(x_n, z_n), 0.0, 1.0)
        t = np.mod(np.arctan2(z_n, x_n), 2.0 * pi)            # 折到 [0, 2π)

        v = np.asarray(profile(SimpleNamespace(r=r, theta=t, alpha=t)), dtype=float)

        I_n = _trapz(v, s_n)                                # ∫v ds(归一化)
        v_bar = I_n / c_n                                     # 弦平均流速

        c_phys = R * c_n
        I_phys = vc * R * I_n                                 # [m^2/s]
        q = None if dz is None else I_phys * dz
        qw = None if omega is None else omega * v_bar * c_n

        return ChordResult(v_bar=v_bar, chord_length=c_phys, line_integral=I_phys,
                           flow_per_dz=I_phys, flow=q, omega_contrib=qw,
                           max_v=float(np.max(v)), d=d, theta_deg=theta_deg)

    def chord_flow_4(self, profile, theta_deg, scheme="Gauss-Jacobi", **kw):
        """四条声道(±内弦、±外弦)的逐条结果与加权总流量(归一化单位 vc*R^2)。"""
        res = []
        for d, w in self.SCHEMES[scheme]:
            for sign in (1.0, -1.0):
                res.append(self.chord_flow(profile, sign * d, theta_deg,
                                           omega=w, **kw))
        q = sum(r.omega_contrib for r in res)
        return res, q

    @staticmethod
    def reference_flow(profile, Nw=801, Nt=720):
        """截面二重积分得到的精确流量(归一化单位 vc*R^2), 作为误差分析的真值。

        用 r = 1 - w^2 换元: (1-r)^(1/n) 在 r->1 处导数无穷, 均匀网格收敛是
        O(h^1.1) 量级(2001 点仍差 2e-4); 换元后被积函数为 w^(2/n), 光滑,
        401 点即可到 1e-5。
        """
        w = np.linspace(0.0, 1.0, Nw)
        t = np.linspace(0.0, 2.0 * pi, Nt)
        WW, TT = np.meshgrid(w, t, indexing="ij")
        RR = 1.0 - WW ** 2
        V = np.asarray(profile(SimpleNamespace(r=RR, theta=TT, alpha=TT)),
                       dtype=float)
        integrand = V * RR * (2.0 * WW)          # v * r * |dr/dw|
        return float(_trapz(_trapz(integrand, t, axis=1), w))

    def error_curve(self, profile, scheme="Gauss-Jacobi", angles=None,
                    N=161, q_ref=None):
        """测量误差随旋转角的变化。

        返回 (angles, eps), eps = (Q_meas - Q_ref) / Q_ref * 100  [%]

        angles : 默认 0°~180° 共 91 点, 也可自行传入
        N      : 每条弦的采样点数(余弦聚集), 161 点误差约 5e-5
        q_ref  : 可外部传入, 避免同一模型重复计算真值
        """
        if angles is None:
            angles = np.linspace(0.0, 180.0, 91)
        angles = np.asarray(angles, dtype=float)
        if q_ref is None:
            q_ref = self.reference_flow(profile, Nw=401, Nt=360)
        eps = np.empty(angles.shape, dtype=float)
        for i, ang in enumerate(angles):
            _, q = self.chord_flow_4(profile, float(ang), scheme, N=N)
            eps[i] = (q - q_ref) / q_ref * 100.0
        return angles, eps

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
        # 圆外置 r=1 (v=0, 反正随后会被掩掉), 避免负底数求分数次幂产生 nan 告警
        prof = SimpleNamespace(r=np.minimum(R, 1.0), theta=T, alpha=T)
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


if __name__ == "__main__":
    fm = flow_measure()
    for idx in (0, 3):
        prof = fm.model_list[idx]
        q_ref = fm.reference_flow(prof)
        print("A%d: Q_ref = %.6f  (单位 Vc*R^2)" % (idx + 1, q_ref))
        for scheme in fm.SCHEMES:
            paths, q = fm.chord_flow_4(prof, 0.0, scheme)
            err = (q - q_ref) / q_ref * 100.0
            vbars = "  ".join("%.4f" % r.v_bar for r in paths)
            print("   %-13s v_bar = [%s]  Q = %.6f  eps = %+.3f%%"
                  % (scheme, vbars, q, err))

