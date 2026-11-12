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