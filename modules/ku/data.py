from datetime import datetime


class Fill:

    def __init__(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()
        self.empty_value = True

    def reset(self):
        self.empty_value = True

    def start(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()

    def stop(self):
        self.t2 = datetime.now()
        self.empty_value = False

    def time(self) -> float:
        return (self.t2 - self.t1).total_seconds()

    def text(self) -> str:
        if self.empty_value:
            return '-'
        if self.result():
            return f'{self.time():.1f}'
        return f'{self.time():.1f} (не норма)'

    def result(self) -> bool:
        return 0 < self.time() <= 3


class Empty:
    def __init__(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()
        self.empty_value = True

    def reset(self):
        self.empty_value = True

    def start(self):
        self.t1 = datetime.now()
        self.t2 = datetime.now()

    def stop(self):
        self.t2 = datetime.now()
        self.empty_value = False

    def time(self) -> float:
        return (self.t2 - self.t1).total_seconds()

    def text(self) -> str:
        if self.empty_value:
            return '-'
        if self.result():
            return f'{self.time():.1f}'
        return f'{self.time():.1f} (не норма)'

    def result(self) -> bool:
        return 0 < self.time() <= 10


class BreakingStage:
    def __init__(self):
        self.p = []
        self.conditions = (
            (0.1, 0.13),
            (0.17, 0.20),
            (0.27, 0.30),
            (0.37, 0.40),
        )

    def reset(self):
        self.p = []

    def append_value(self, value: float):
        self.p.append(value)

    def stage_result(self, stage: int) -> bool:
        if not self.p: return False
        if stage >= len(self.p): return False
        if not self.p[stage]: return False

        return self.conditions[stage][0] <= self.p[stage] <= self.conditions[stage][1]

    def result(self) -> bool:
        return all([self.stage_result(stage) for stage in range(4)])

    def text(self, stage: int) -> str:
        if not self.p: return '-'
        if stage >= len(self.p): return '-'
        if not self.p[stage]: return '-'
        if self.stage_result(stage):
            return f'{self.p[stage]:.3f}'
        else:
            return f'{self.p[stage]:.3f} (не норма)'


class Sensitivity:
    def __init__(self):
        self.p = []

    def reset(self):
        self.p = []

    def update(self, value: float):
        self.p.append(value)

    def dp(self) -> float:
        if not self.p: return -1
        return max(self.p) - min(self.p)

    def result(self) -> bool:
        return 0 <= self.dp() <= 0.015

    def text(self) -> str:
        if not self.p: return '-'
        if self.result():
            return f'{self.dp():.3f}'
        else:
            return f'{self.dp():.3f} (не норма)'


class Junctions:
    def __init__(self):

        self.value = False
        self.empty = True

    def reset(self):
        self.empty = True
        self.value = False

    def result(self) -> bool:
        return not self.empty and self.value

    def text(self) -> str:
        if self.empty: return '-'
        if self.result():
            return f'норма'
        else:
            return f'не норма'

    def fail(self):
        self.value = False
        self.empty = False

    def success(self):
        self.value = True
        self.empty = False


class Valve:
    def __init__(self):
        self.value = False
        self.empty = True

    def reset(self):
        self.empty = True
        self.value = False

    def result(self) -> bool:
        return not self.empty and self.value

    def text(self) -> str:
        if self.empty: return '-'
        if self.result():
            return f'норма'
        else:
            return f'не норма'

    def fail(self):
        self.value = False
        self.empty = False

    def success(self):
        self.value = True
        self.empty = False


class KuData:
    def __init__(self):
        self.fill = Fill()
        self.empty = Empty()
        self.breaking_stage = BreakingStage()
        self.sensitivity = Sensitivity()
        self.valve = Valve()
        self.junctions = Junctions()
