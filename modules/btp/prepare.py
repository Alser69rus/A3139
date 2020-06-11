from PyQt5.QtCore import QState, QFinalState, QEvent, pyqtSignal, pyqtBoundSignal
from controller.controller import Controller

ctrl: Controller


class Prepare(QState):
    def __init__(self, controller: Controller, menu_state: QState):
        super().__init__(parent=controller.stm)
        global ctrl
        ctrl = controller
        self.finish = QFinalState(self)
        self.addTransition(self.finished, menu_state)
        menu = ctrl.menu.menu['БТП 020']
        self.addTransition(ctrl.button['back'].clicked, self.finish)
        menu_state.addTransition(menu.button['Подготовка'].clicked, self)

        self.start = Start(self)
        self.check_pim = CheckPim(self)
        self.check_tank = CheckTank(self)
        self.check_zam_el_torm = CheckZamElTorm(self)
        self.check_speed_60 = CheckSpeed60(self)
        self.set_bto = SetBTO(self)
        self.enter_vr = EnterVr(self)
        self.btp_to_stand = BtpToStand(self)

        self.setInitialState(self.start)
        self.start.addTransition(ctrl.switch['ku 215'].high_value, self.check_pim)
        self.check_pim.addTransition(ctrl.server_updated, self.check_pim)
        self.check_pim.addTransition(self.check_pim.done, self.check_tank)
        self.check_tank.addTransition(ctrl.switch_with_neutral['tank'].state_two, self.check_zam_el_torm)
        self.check_zam_el_torm.addTransition(ctrl.switch['el. braking'].low_value, self.check_speed_60)
        self.check_speed_60.addTransition(ctrl.switch['>60 km/h'].low_value, self.set_bto)
        self.set_bto.addTransition(ctrl.button['yes'].clicked, self.enter_vr)
        self.enter_vr.addTransition(ctrl.switch_with_neutral['enter'].state_one, self.btp_to_stand)
        self.btp_to_stand.addTransition(ctrl.button['yes'].clicked, self.finish)


class Start(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.show_panel('манометры текст')
        ctrl.button_enable('back')
        text = f'<p><font color="red">ВНИМАНИЕ! БТО испытывается с исправным КУ 215.</font></p>' \
               f'<p>Установите КУ 215 на прижим, включите пневмотумблер "ПРИЖИМ КУ 215".</p>' \
               f'<p>Включите тумблер "КУ 215".</p>'

        ctrl.setText(text)


class CheckPim(QState):
    done = pyqtSignal()

    def onEntry(self, event: QEvent) -> None:
        text = f'<p>Необходимо сбросить до нуля давление в импульсной магистрали. ' \
               f'Для этого переведите ручку крана в отпускное положение.</p>'

        ctrl.setText(text)
        if ctrl.manometer['p im'].get_value() < 0.005:
            self.done.emit()


class CheckTank(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back yes')
        ctrl.setText(f'<p>Включите тумблер "НАКОП. РЕЗ." в положение "СБРОС".</p>')


class CheckZamElTorm(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back')
        text = f'<p>Выключите тумблер "ЗАМ. ЭЛ. ТОРМ."</p>'
        ctrl.setText(text)


class CheckSpeed60(QState):
    def onEntry(self, event: QEvent) -> None:
        text = f'<p>Выключите тумблер "> 60 км/ч"</p>'
        ctrl.setText(text)


class SetBTO(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back yes')
        text = f'<p>Установите БТО на стойку.</p>' \
               f'<p>Установите тумблером "50 В - 100 В" напряжение, соответствующее рабочему напряжению БТО.</p>' \
               f'<p>Подключите электрические шлейфы от стенда к БТО.</p><p>Подключите пневматические рукава к БТО.</p>' \
               f' <p><br>Для продолжения нажмите "ДА".</p>'
        ctrl.setText(text)


class EnterVr(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back')
        text = f'<p>Включите тумблер "ВХОД" в положение "ВР".</p>'
        ctrl.setText(text)


class BtpToStand(QState):
    def onEntry(self, event: QEvent) -> None:
        ctrl.button_enable('back yes')
        text = f'<p>Включите пневмотумблер "БТП К СТЕНДУ".</p>' \
               f'<p><br>Для продолжения нажмите "ДА".</p>'
        ctrl.setText(text)
        ctrl.menu.current_menu.current_button.set_success()
