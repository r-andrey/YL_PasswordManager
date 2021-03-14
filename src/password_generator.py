"""
password_generator.py

andrey.rudin@gmail.com
"""

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
from random import choices

from settings import Settings


class PasswordGenerator(QDialog):
    def __init__(self):
        super().__init__()

        uic.loadUi("ui/password_generator.ui", self)

        self.__settings = Settings()
        self.spinBoxLength.setValue(self.__settings.password_len)
        self.cbLat1.setChecked(self.__settings.lat1)
        self.cbLat2.setChecked(self.__settings.lat2)
        self.cbNumbers.setChecked(self.__settings.numbers)
        self.cbSpecial.setChecked(self.__settings.special)
        self.cbAmbiguous.setChecked(self.__settings.ambiguous)

        self.btnGenerate.clicked.connect(self.btnGenerate_click)
        self.cbLat1.stateChanged.connect(self.cbStateChanged)
        self.cbLat2.stateChanged.connect(self.cbStateChanged)
        self.cbNumbers.stateChanged.connect(self.cbStateChanged)
        self.cbSpecial.stateChanged.connect(self.cbStateChanged)
        self.cbAmbiguous.stateChanged.connect(self.cbStateChanged)

        self.spinBoxLength.valueChanged.connect(self.sbValueChange)

        self.btnGenerate_click()

    def btnGenerate_click(self):
        self.editPassword.setText(self.generate())

    def cbStateChanged(self):
        self.__settings.lat1 = True if self.cbLat1.isChecked() else False
        self.__settings.lat2 = True if self.cbLat2.isChecked() else False
        self.__settings.numbers = True if self.cbNumbers.isChecked() else False
        self.__settings.special = True if self.cbSpecial.isChecked() else False
        self.__settings.ambiguous = True if self.cbAmbiguous.isChecked() else False

    def sbValueChange(self):
        self.__settings.password_len = self.spinBoxLength.value()

    def generate(self):
        abc = ""

        lat1Abc = "qwertyuiopasdfghjklzxcvbnm"
        lat2Abc = "QWERTYUIOPASDFGHJKLZXCVBNM"
        numbersAbc = "0123456789"
        specialAbc = "!@#$%^&*"

        if self.cbLat1.isChecked():
            abc += lat1Abc

        if self.cbLat2.isChecked():
            abc += lat2Abc

        if self.cbNumbers.isChecked():
            abc += numbersAbc

        if self.cbSpecial.isChecked():
            abc += specialAbc

        if self.cbAmbiguous.isChecked():
            for ch in "IlO01!":
                abc = abc.replace(ch, "")

        while True:
            result = "".join(choices(abc, k=self.spinBoxLength.value()))
            if self.cbLat1.isChecked():
                if not any([ch in result for ch in lat1Abc]):
                    continue

            if self.cbLat2.isChecked():
                if not any([ch in result for ch in lat2Abc]):
                    continue

            if self.cbNumbers.isChecked():
                if not any([ch in result for ch in numbersAbc]):
                    continue

            if self.cbSpecial.isChecked():
                if not any([ch in result for ch in specialAbc]):
                    continue

            break

        return result
