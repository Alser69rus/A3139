from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from ui.button_panel import ButtonPanel
from ui.workspace import Workspace
from ui.manometers_panel import Manometers
from PyQt5 import QtGui


class MainForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.resize(1024, 768)
        self.setWindowTitle('Стенд А3139')

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setContentsMargins(4, 4, 4, 4)
        self.manometers = Manometers()
        self.workspace = Workspace()
        self.btn_panel = ButtonPanel()

        self.setLayout(self.vbox)
        self.vbox.addWidget(self.manometers)
        self.vbox.addWidget(self.workspace)
        self.vbox.addWidget(self.btn_panel)

        # todo 2 Создать меню
        # todo 2.4 напполнить меню для проекта и расположить его на форме
        # todo 2.5 сделать навигацию по меню

        # todo 7 Создать виджет заполнения формы испытания
        # todo 8Создать виджет отчета

    @pyqtSlot(str)
    def show_panel(self, value: str):
        available_panel = {
            'манометры': self.manometers,
            'меню': self.workspace.menu,
            'текст': self.workspace.text,
            'картинка': self.workspace.img,
            'график': self.workspace.graph,
            'настройки': self.workspace.settings,
            'заголовок': self.workspace.report_header,
            'отчет': self.workspace.report,
        }
        for panel in available_panel.keys():
            available_panel[panel].setVisible(panel in value)
