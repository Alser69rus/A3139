from datetime import datetime


class KU215:
    def __init__(self):
        self.handle = (
            '1 ступень',
            '2 ступень',
            '3 ступень',
            '4 ступень',
            '3 ступень',
            '2 ступень',
            '1 ступень',
            'отпуск',
        )
        self.range = (
            (0.10, 0.13),
            (0.17, 0.20),
            (0.27, 0.30),
            (0.37, 0.40),
            (0.27, 0.30),
            (0.17, 0.20),
            (0.10, 0.13),
            (0.0, 0.005),
        )


class Breaking:
    def __init__(self):
        self.tc = [[-1.0] * 8, [-1.0] * 8]
        self.ku_215: KU215 = KU215()

    def position_as_text(self, position: int):
        return self.ku_215.handle[position]

    def range_as_text(self, position: int) -> str:
        low, high = self.ku_215.range[position]
        return f'{low:.3f} - {high:.3f}'

    def tc_as_text(self, tc: int, position: int) -> str:
        value: float = self.tc[tc][position]
        low, high = self.ku_215.range[position]
        if value < -0.1:
            return '-'
        elif low <= value <= high:
            return f'{value:5.3f}'
        else:
            return f'{value:5.3f} (не норма)'

    def success(self) -> bool:
        res = []
        for i in range(8):
            low, high = self.ku_215.range[i]
            res.append(low <= self.tc[0][i] <= high)
            res.append(low <= self.tc[1][i] <= high)
        return all(res)


class FillTime:
    def __init__(self):
        self.tc = [0.0, 0.0]
        self.t = [datetime.now(), datetime.now()]
        self.running = [False, False]

    def start(self):
        self.tc = [0.0, 0.0]
        self.t = [datetime.now(), datetime.now()]
        self.running = [True, True]

    def stop(self, tc: int):
        if self.running[tc]:
            self.running[tc] = False
            self.tc[tc] = (datetime.now() - self.t[tc]).total_seconds()

    def success(self) -> bool:
        return all([0.05 < t <= 4 for t in self.tc])

    def time_as_text(self, tc: int) -> str:
        value = self.tc[tc]
        if value < 0.05:
            return '-'
        elif 0 < value <= 4:
            return f'{value:.1f}'
        else:
            return f'{value:.1f} (не норма)'


class EmptyTime:
    def __init__(self):
        self.tc = [0.0, 0.0]
        self.t = [datetime.now(), datetime.now()]
        self.running = [False, False]

    def start(self, tc: int):
        self.tc[tc] = 0.0
        self.t[tc] = datetime.now()
        self.running[tc] = True

    def stop(self, tc: int):
        if self.running[tc]:
            self.running[tc] = False
            self.tc[tc] = (datetime.now() - self.t[tc]).total_seconds()

    def success(self) -> bool:
        return all([0.05 < t <= 13 for t in self.tc])

    def time_as_text(self, tc: int) -> str:
        t: float = self.tc[tc]
        if t < 0.05:
            return '-'
        elif 0 < t <= 13:
            return f'{t:.1f}'
        else:
            return f'{t:.1f} (не норма)'


class BtpData:
    def __init__(self):
        self.ku_215: KU215 = KU215()
        self.auto_breaking: Breaking = Breaking()
        self.kvt_breaking: Breaking = Breaking()
        self.fill_time: FillTime = FillTime()
        self.empty_time: EmptyTime = EmptyTime()
        self.tightness: str = '-'
        self.substitution: FillTime = FillTime()
        self.speed_fill: FillTime = FillTime()
        self.speed_empty: EmptyTime = EmptyTime()
        self.sped_ok = ['-', '-']
