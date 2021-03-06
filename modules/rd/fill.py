from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal

from controller.controller import Controller
from modules.rd.common import Common

ctrl: Controller


class Fill(QState):
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
        parent.menu.addTransition(menu.button['Время наполнения'].clicked, self)

        self.start = Start(self)
        self.rdkp_0 = Rdkp0(self)
        self.upr_rd_off = UprRdOff(self)
        self.ptc = Ptc(self)
        self.set_ptc = SetPtc(self)
        self.pressure_check = common.PressureCheck(self)
        self.rdkp_rd = RdkpRd(self)
        self.upr_rd_on = UprRdOn(self)
        self.measure = Measure(self)
        self.show_result = ShowResult(self)

        self.setInitialState(self.start)
        self.start.addTransition(self.pressure_check)
        self.pressure_check.addTransition(self.pressure_check.finished, self.upr_rd_off)
        self.upr_rd_off.addTransition(ctrl.switch['upr rd 042'].low_value, self.ptc)
        self.ptc.addTransition(self.ptc.success, self.upr_rd_on)
        self.ptc.addTransition(self.ptc.fail, self.set_ptc)
        self.set_ptc.addTransition(ctrl.server_updated, self.set_ptc)
        self.set_ptc.addTransition(ctrl.button['yes'].clicked, self.upr_rd_on)
        self.upr_rd_on.addTransition(ctrl.switch['upr rd 042'].high_value, self.measure)
        self.measure.addTransition(ctrl.server_updated, self.measure)
        self.measure.addTransition(self.measure.done, self.show_result)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.graph.show_graph('p im p tc2')
        ctrl.show_button('back')
        ctrl.normal()
        ctrl.rd.fill.reset()


class Rdkp0(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Включите тумблер "РД 042 - 0 - КП 106 (КЭБ 208)" в положение "- 0 -".')


class UprRdOff(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Выключите тумблер "УПР. РД 042".')


class Ptc(QState):
    success = pyqtSignal()
    fail = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.show_button('back')
        ctrl.setText('Проверка давления в магистрали ТЦ2, норма 0 МПа.')
        if ctrl.manometer['p tc2'].get_value() <= 0.005:
            self.success.emit()
        else:
            self.fail.emit()


class SetPtc(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('<p>Сбросьте давление в магистрали ТЦ2 до 0 МПа.</p>'
                     '<p><br>Для продолжения нажмите "ДА".</p>')
        if ctrl.manometer['p tc2'].get_value() <= 0.005:
            ctrl.show_button('back yes')
        else:
            ctrl.show_button('back')


class RdkpRd(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.show_button('back')
        ctrl.setText('<p>Включите тумблер "РД 042 - 0 - КП 106 (КЭБ 208)" в положение "РД 042".</p>')

    def onExit(self, event: QEvent) -> None:
        ctrl.graph.start()
        ctrl.rd.fill.start()


class UprRdOn(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст график')
        ctrl.show_button('back')
        ctrl.setText('Включите тумблер "УПР. РД 042".')

    def onExit(self, event: QEvent) -> None:
        ctrl.graph.start()
        ctrl.rd.fill.start()


class Measure(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        ctrl.setText('Производится измерение времени наполнения ТЦ2 с 0 до 0,35 МПа.')
        ctrl.graph.update()
        ctrl.rd.fill.update()
        p = ctrl.manometer['p tc2'].get_value()
        t = ctrl.graph.dt
        if t > 20 or p >= 0.35:
            self.done.emit()


class ShowResult(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('текст график')
        ctrl.show_button('back')
        if ctrl.rd.fill.result():
            ctrl.success()
        else:
            ctrl.fail()

        t = ctrl.rd.fill.text()

        ctrl.setText(f'<p><table border="2" cellpadding="4">'
                     f'<caption>Проверка времмени наполнения ТЦ (торможение)</caption>'
                     f'<tr><th>Наименование</th><th>Норма, c</th><th>ТЦ2 факт, с</th></tr>'
                     f'<tr><td>Время наполнения ТЦ2<br>(с 0 до 0,35 МПа)</td><td>не более 4</td>'
                     f'<td align="center">{t}</td></tr>'
                     f'</table></p>'
                     f'<p><br>Для продолжения нажмите "ВОЗВРАТ".</p>')
