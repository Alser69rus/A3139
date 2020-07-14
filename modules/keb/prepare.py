from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal, pyqtBoundSignal
from controller.controller import Controller
from modules.keb.common import ResetPtc, PreparePressure


class Prepare(QState):
    def __init__(self, parent):
        super().__init__(parent=parent.controller.stm)

        self.controller: Controller = parent.controller
        ctrl = self.controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent.menu)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['КЭБ 208']
        parent.menu.addTransition(menu.button['Подготовка к испытанию'].clicked, self)

        self.start = Start(self)
        self.install_rd = InstallRd(self)
        self.reset_ptc = ResetPtc(self)
        self.voltage = Voltage(self)
        self.install_keb = InstallKeb(self)
        self.prepare_pressure = PreparePressure(self)
        self.enable_menu = EnableMenu(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.install_rd)
        self.install_rd.addTransition(ctrl.button['yes'].clicked, self.reset_ptc)
        self.reset_ptc.addTransition(self.reset_ptc.finished, self.voltage)
        self.voltage.addTransition(ctrl.button['yes'].clicked, self.install_keb)
        self.install_keb.addTransition(ctrl.button['yes'].clicked, self.prepare_pressure)
        self.prepare_pressure.addTransition(self.prepare_pressure.finished, self.enable_menu)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back')
        ctrl.normal()


class InstallRd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.show_button('back yes')
        ctrl.setText('<p><font color="red">ВНИМАНИЕ! КЭБ 208 испытывается с исправным РД 042.</font></p>'
                     '<p>Установите РД 042 на прижим, включите пенвмотумблер "ПРИЖИМ РД 042".</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')


class Voltage(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.show_button('back yes')
        ctrl.setText('<p>Установите тумблером "50 В - 110 В" напряжение, соответствующее '
                     'рабочему напряжению КЭБ 208.</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')


class InstallKeb(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.show_button('back yes')
        ctrl.setText('<p>Установите КЭБ 208 на прижим, включите пневмотумблер "ПРИЖИМ КЭБ 208".</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')


class EnableMenu(QFinalState):
    def onEntry(self, event: QEvent) -> None:
        ctrl: Controller = self.parent().controller
        ctrl.success()
        menu = ctrl.menu.menu['РД 042']
        buttons = [
            'Время наполнения',
            'Поддержание давления',
            'Время отпуска',
            'Герметичность соединений',
            'Герметичность клапана',
            'Завершение',
        ]
        for name in buttons:
            menu.button[name].setEnabled(True)
