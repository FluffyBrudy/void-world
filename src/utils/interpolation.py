class SimpleInterpolation:
    __slots__ = ("current", "target", "speed")

    def __init__(self, value: float = 1.0, speed: float = 0.1) -> None:
        self.current = value
        self.target = value
        self.speed = speed

    def set(self, target: float):
        self.target = max(0, min(target, 1.0))

    def update(self):
        diff = self.target - self.current
        if abs(diff) < 0.001:
            self.current = self.target
        else:
            self.current += diff * self.speed
