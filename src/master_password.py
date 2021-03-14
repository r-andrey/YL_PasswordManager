"""
master_password.py

andrey.rudin@gmail.com
"""

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox

from settings import Settings


def show_message(text: str):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Warning)
    msgBox.setText(text)
    msgBox.setWindowTitle("Сообщение")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()


class MasterPassword(QDialog):
    def __init__(self):
        super().__init__()

        self.__settings = Settings()

        uic.loadUi("ui/master_password.ui", self)

        self.master_password = None
        self.btnCancel.clicked.connect(self.btnCancel_click)
        self.btnOK.clicked.connect(self.btnOK_click)

    def btnCancel_click(self):
        self.close()

    def btnOK_click(self):
        if len(self.editMasterPassword.text()) < self.__settings.min_length:
            show_message(f"Минимальная длина пароля {self.__settings.min_length} символов")
            return

        if self.editMasterPassword.text() != self.editConfirmMasterPassword.text():
            show_message("Пароли не совпадают")
            return

        self.master_password = self.editMasterPassword.text()

        self.close()
