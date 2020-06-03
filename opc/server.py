from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread, Qt, QSettings
from datetime import datetime
from pymodbus.client.sync import ModbusSerialClient as Client
from opc.owen import MV110_16D, MV110_8AC, MV110_32DN,MV_DI
from typing import Dict
from opc.opc import AnalogItemType, TwoStateDiscreteType, Range

UPDATE_DELAY = 50


class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.running: bool = True
        self.client = Client(method='rtu', port='COM9', timeout=0.05, baudrate=115200, retry_on_empty=True)
        self.ai: MV110_8AC = MV110_8AC(client=self.client, unit=16)
        self.load_ai_settings()
        self.di: MV_DI = MV110_32DN(client=self.client, unit=2)
        self.ai.pin[1].eu_range = Range(0, 1)

    def load_ai_settings(self):
        settings = QSettings('Настройки.ini', QSettings.IniFormat)
        settings.setIniCodec('UTF-8')
        for i in range(5):
            self.ai.pin[i].eu_range = Range(0, float(settings.value(f'Manometers/m{i}')))

    @pyqtSlot()
    def do_work(self):
        while self.running:
            t = datetime.now()
            # self.ai.update()
            # self.di.update()
            t = (datetime.now() - t).total_seconds()
            t = round(UPDATE_DELAY - t * 1000)
            if t > 0:
                self.thread().msleep(t)
        self.finished.emit()

    @pyqtSlot()
    def stop(self):
        self.running = False


class Server(QObject):
    stop_all = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.th: QThread = QThread()
        self.worker: Worker = Worker()
        self.worker.moveToThread(self.th)
        self.th.started.connect(self.worker.do_work)
        self.worker.finished.connect(self.th.quit)
        self.stop_all.connect(self.worker.stop, Qt.DirectConnection)
        # self.worker.finished.connect(self.worker.deleteLater)
        # self.th.finished.connect(self.th.deleteLater)

        self.ai: Dict[str, AnalogItemType] = {'ppm': self.worker.ai.pin[0],
                                              'pim': self.worker.ai.pin[1],
                                              'ptc1': self.worker.ai.pin[2],
                                              'ptc2': self.worker.ai.pin[3],
                                              'pupr': self.worker.ai.pin[4], }
        self.di: Dict[str, TwoStateDiscreteType] = {'back': self.worker.di.pin[0],
                                                    'up': self.worker.di.pin[1],
                                                    'down': self.worker.di.pin[2],
                                                    'yes': self.worker.di.pin[3],
                                                    'no': self.worker.di.pin[4],
                                                    'rd 042': self.worker.di.pin[5],
                                                    'upr rd 042': self.worker.di.pin[6],
                                                    '0 - rd 042': self.worker.di.pin[7],
                                                    '0 - keb 208': self.worker.di.pin[8],
                                                    'tc2 8-20': self.worker.di.pin[9],
                                                    'leak 1': self.worker.di.pin[10],
                                                    'leak 0,5': self.worker.di.pin[11],
                                                    'accumulator tank': self.worker.di.pin[12],
                                                    # 'enter': self.worker.di.pin[13]
                                                    'ku 215': self.worker.di.pin[14],
                                                    'sub. el. braking': self.worker.di.pin[15],
                                                    '>60 km/h': self.worker.di.pin[5],
                                                    'ok': self.worker.di.pin[5],
                                                    '0- vr': self.worker.di.pin[5],
                                                    '0- ku': self.worker.di.pin[5],
                                                    'keb 208': self.worker.di.pin[5],
                                                    'red 211': self.worker.di.pin[5],
                                                    'examination': self.worker.di.pin[5],
                                                    }

        '''

13.	Тумблер «КЭБ 208 - ВЫКЛ» (1 сигнал «есть или нет»).
14.	Тумблер «РЕД 211 - ВЫКЛ» (1 сигнал «есть или нет»).
15.	Кнопка «ВОЗВРАТ» (1 сигнал «есть или нет»).
16.	Кнопка «ВВЕРХ - ВНИЗ» (2 сигнала).
17.	Кнопка «ДА» (1 сигнал «есть или нет»).
18.	Кнопка «НЕТ» (1 сигнал «есть или нет»).
19.	Кнопка «ИСПЫТАНИЕ» (1 сигнал «есть или нет») под вопросом, но лучше заведи сигнал может пригодится.

        '''

        self.th.start()
