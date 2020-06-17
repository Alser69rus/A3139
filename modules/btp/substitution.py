from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.btp.common import Common

ctrl: Controller


class Substitution(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        common = Common(controller=ctrl)
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu = ctrl.menu.menu['БТП 020']
        menu_state.addTransition(menu.button['Замещение торможения'].clicked, self)

        self.start = Start(self)
        self.ppm = common.Ppm(self)
        self.el_breaking = common.ElBreaking(self)
        self.speed_60 = common.Speed60(self)
        self.ku_215 = common.KU215(self)
        self.pim = common.Pim(self)
        self.enter = common.Enter(state='- 0 -', parent=self)
        self.el_breaking_on = ElBreakingOn(self)
        self.measure = Measure(self)
        self.el_breaking_off = ElBreakingOff(self)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.ppm)
        self.ppm.addTransition(ctrl.server_updated, self.ppm)
        self.ppm.addTransition(self.ppm.done, self.el_breaking)
        self.el_breaking.addTransition(ctrl.switch['el. braking'].low_value, self.speed_60)
        self.speed_60.addTransition(ctrl.switch['>60 km/h'].low_value, self.ku_215)
        self.ku_215.addTransition(ctrl.switch['ku 215'].high_value, self.pim)
        self.pim.addTransition(ctrl.server_updated, self.pim)
        self.pim.addTransition(self.pim.done, self.enter)
        self.enter.addTransition(ctrl.switch_with_neutral['enter'].state_neutral, self.el_breaking_on)
        self.el_breaking_on.addTransition(ctrl.server_updated, self.el_breaking_on)
        self.el_breaking_on.addTransition(ctrl.switch['el. braking'].high_value, self.measure)
        self.measure.addTransition(ctrl.server_updated, self.measure)
        self.measure.addTransition(self.measure.done, self.el_breaking_off)
        self.el_breaking_off.addTransition(ctrl.switch['el. braking'].low_value, self.show_result)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p im p tc1 p tc2')
        ctrl.graph.reset()
        ctrl.button_enable('back')
        ctrl.menu.current_menu.current_button.set_normal()


class ElBreakingOn(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'Включите тумблер "ЗАМ. ЭЛ. ТОРМ."')
        ctrl.graph.start()
        ctrl.btp.substitution.start()


class Measure(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.graph.update()
        tc1 = ctrl.manometer['p tc1'].get_value()
        tc2 = ctrl.manometer['p tc2'].get_value()
        t = ctrl.graph.dt
        ctrl.setText(f'<p>Производится измерение времени наполнения ТЦ1 и ТЦ 2 до 0,16 МПа.</p>')

        if tc1 >= 0.16:
            ctrl.btp.substitution.stop(0)
        if tc2 >= 0.16:
            ctrl.btp.substitution.stop(1)
        if tc1 >= 0.16 and tc2 >= 0.16 or t > 8:
            self.done.emit()


class ElBreakingOff(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText(f'Выключите тумблер "ЗАМ. ЭЛ. ТОРМ."')


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('текст')
        ctrl.button_enable('back')
        data = ctrl.btp.substitution
        tc1 = data.time_as_text(0)
        tc2 = data.time_as_text(1)
        ctrl.setText(f'<p><table border="2" cellpadding="4">'
                     f'<caption>Проверка раблоты БТО при замещении'
                     f' электрического торможения</caption>'
                     f'<tr><th>Наименование</th><th>Норма, МПа</th><th>ТЦ1 факт, с</th><th>ТЦ2 факт, с</th></tr>'
                     f'<tr><td>Время наполнения ТЦ при замещении<br>электрического торможения'
                     f'<br>(с 0 до 0,16 МПа)</td><td>не более 4 с</td>'
                     f'<td align="center">{tc1}</td><td align="center">{tc2}</td></tr>'
                     f'</table></p>'
                     f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>')
        if data.success():
            ctrl.menu.current_menu.current_button.set_success()
        else:
            ctrl.menu.current_menu.current_button.set_fail()
