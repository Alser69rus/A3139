from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Union

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtCore import QStateMachine
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPushButton, QLabel, QWidget

from modules.btp.data import BtpData
from modules.keb.data import KebData
from modules.ku.data import KuData
from modules.rd.data import RdData
from opc.opc import TwoStateDiscreteType
from opc.server import Server
from ui.graph_widget import Plot
from ui.main_form import MainForm
from ui.main_menu import MainMenu

ANIMATE_CLICK_DELAY = 50


class ReportHeader:
    def __init__(self):
        self.dev_num = ''
        self.date = ''
        self.locomotive = ''
        self.section = ''
        self.name_1 = ''
        self.name_2 = ''
        self.today = datetime.today()


class Controller(QObject):
    close_all = pyqtSignal()
    server_updated = pyqtSignal()

    def __init__(self, server: Server, form: MainForm, stm: QStateMachine, parent=None):
        super().__init__(parent=parent)
        self.server = server
        self.form = form
        self.stm = stm

        self.menu: MainMenu = form.workspace.menu
        self.text: QLabel = form.workspace.text
        self.image: QLabel = form.workspace.img
        self.graph: Plot = form.workspace.graph
        self.images: Dict[str, QPixmap] = form.workspace.img.images
        self.ctrl_win: QWidget = form.ctrl_win
        self.diag_win: QWidget = form.diag_win
        self.report = form.workspace.report

        self.show_panel = form.show_panel
        self.show_menu = self.menu.show_menu
        self.reset_prepare = self.menu.reset_prepare
        self.show_button = self.form.button_panel.show_button
        self.setText = self.text.setText

        self.form.closeEvent = self.closeEvent
        self.close_all.connect(self.ctrl_win.close)
        self.close_all.connect(self.diag_win.close)
        self.server.worker.updated.connect(self.server_updated)

        self.button: Dict[str, Union[TwoStateDiscreteType, QPushButton]] = {}
        panel_buttons = self.form.button_panel.button.keys()
        server_buttons = server.button.keys()
        for key in server_buttons:
            if key in panel_buttons:
                self.button[key] = form.button_panel.button[key]
            else:
                self.button[key] = server.button[key]

        self.manometer = server.manometer
        self.switch = server.switch
        self.switch_with_neutral = server.switch_with_neutral
        # self.manom = server.manom
        # self.switc = server.switc
        # self.multi_switch = server.multi_switch

        self.report_header = ReportHeader()
        self.btp = BtpData()
        self.rd = RdData()
        self.keb = KebData()
        self.ku = KuData()

    def closeEvent(self, QCloseEvent):
        running_states = [self.server.th.isRunning(), self.stm.isRunning()]
        self.server.stop_all.emit()
        self.stm.stop()
        self.close_all.emit()
        if any(running_states):
            QTimer.singleShot(500, self.form.close)
            QCloseEvent.ignore()
        else:
            QCloseEvent.accept()

    def update_report_header(self):
        field = self.menu.prepare_menu.get_data_fields()
        self.report_header = ReportHeader()
        self.report_header.dev_num = field[0]
        self.report_header.date = field[1]
        self.report_header.locomotive = field[2]
        self.report_header.section = field[3]
        self.report_header.name_1 = field[4]
        self.report_header.name_2 = field[5]

    def normal(self):
        self.menu.current_menu.current_button.set_normal()

    def success(self):
        self.menu.current_menu.current_button.set_success()

    def fail(self):
        self.menu.current_menu.current_button.set_fail()
