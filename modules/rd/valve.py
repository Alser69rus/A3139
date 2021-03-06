from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.rd.common import Common

ctrl: Controller


class Valve(QState):
    def __init__(self, parent):
        super().__init__(parent=parent.controller.stm)
        global ctrl
        self.controller: Controller = parent.controller
        ctrl = self.controller
        common = Common(self)
        self.finish = QFinalState(self)
        self.addTransition(self.finished, parent.menu)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['РД 042']
        parent.menu.addTransition(menu.button['Герметичность клапана'].clicked, self)

        self.start = Start(self)
        self.pressure_check = common.PressureCheck(self)
        self.upr_rd = UprRd(self)
        self.rdkp_rd=RdkpRd(self)
        self.ptc = Ptc(self)
        self.set_ptc = SetPtc(self)
        self.valve_check = ValveCheck(self)
        self.valve_success = ValveSuccess(self)
        self.valve_fail = ValveFail(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.pressure_check)
        self.pressure_check.addTransition(self.pressure_check.finished, self.upr_rd)
        self.upr_rd.addTransition(ctrl.switch['upr rd 042'].high_value, self.rdkp_rd)
        self.rdkp_rd.addTransition(ctrl.switch_with_neutral['rd-0-keb'].state_one,self.ptc)
        self.ptc.addTransition(self.ptc.success, self.valve_check)
        self.ptc.addTransition(self.ptc.fail, self.set_ptc)
        self.set_ptc.addTransition(ctrl.server_updated, self.set_ptc)
        self.set_ptc.addTransition(ctrl.button['yes'].clicked, self.valve_check)
        self.valve_check.addTransition(ctrl.button['yes'].clicked, self.valve_success)
        self.valve_check.addTransition(ctrl.button['no'].clicked, self.valve_fail)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back')
        ctrl.normal()
        ctrl.rd.valve = '-'


class UprRd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back')
        ctrl.setText('Включите тумблер "УПР. РД 042".')


class RdkpRd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.show_button('back')
        ctrl.setText('Включите тумблер "РД 042 - 0 - КЭБ 208" в положение "РД 042".')


class Ptc(QState):
    success = pyqtSignal()
    fail = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Проверка давления в ТЦ2. Норма: не менее 0,35 Мпа.')
        if ctrl.manometer['p tc2'].get_value() >= 0.35:
            self.success.emit()
        else:
            self.fail.emit()


class SetPtc(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('<p>Установите давление в ТЦ 2 не менее 0,35 МПа.</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')
        if ctrl.manometer['p tc2'].get_value() >= 0.35:
            ctrl.show_button('back yes')
        else:
            ctrl.show_button('back')


class ValveCheck(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_button('back yes no')
        ctrl.setText('<p>Обмыльте мыльным раствором атмосферный клапан.</p>'
                     '<p>Норма: пропуск воздуха не допускается.</p>'
                     '<p><br>Если это обеспечивается - нажмите "ДА".</p>'
                     '<p>В противном случае нажмите "НЕТ".</p>')


class ValveSuccess(QFinalState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.success()
        ctrl.rd.valve = 'норма'


class ValveFail(QFinalState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.fail()
        ctrl.rd.valve = 'не норма'
