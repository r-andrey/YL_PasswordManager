"""
main.py

andrey.rudin@gmail.com
"""

import sys
import json

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QListWidgetItem
from json import JSONEncoder
from uuid import UUID, uuid4

from crypto_file import CryptoFile, InvalidFormatException, InvalidPasswordException
from settings import Settings

from password_generator import PasswordGenerator
from master_password import MasterPassword


def show_message(text: str):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Warning)
    msgBox.setText(text)
    msgBox.setWindowTitle("Сообщение")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()


class Password:
    def __init__(self, title: str, site: str, login: str, password: str, additional: str, uuid: UUID = uuid4()):
        self.uuid = str(uuid)
        self.title = title
        self.site = site
        self.login = login
        self.password = password
        self.additional = additional

    @classmethod
    def from_json(cls, data: json):
        return cls(uuid=data["uuid"],
                   title=data["title"],
                   site=data["site"],
                   login=data["login"],
                   password=data["password"],
                   additional=data["additional"])


# Ожидается следующей версии :)
class Page:
    def __init__(self, title: str, content: str, uuid: UUID = uuid4()):
        self.uuid = uuid
        self.title = title
        self.content = content

    @classmethod
    def from_json(cls, data: json):
        return cls(uuid=data["uuid"],
                   title=data["title"],
                   content=data["content"])


class ClassEncoder(JSONEncoder):
    def default(self, obj):
        return obj.__dict__


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.__settings = Settings()
        self.__master_password = None
        self.__passwords = dict()
        self.__pages = dict()
        self.__password_uuid = None
        self.__edit_mode = False
        self.__page_id = 0

        uic.loadUi("ui/main_form.ui", self)

        self.setWindowTitle(f"{self.__settings.title} {self.__settings.version}")

        self.__password_generator = PasswordGenerator()

        if self.__settings.file_name:
            self.__page_id = 0
            self.__set_edit_mode(False)
        else:
            self.__page_id = 1

        self.stackedWidget.setCurrentIndex(self.__page_id)

        self.btnSelectFileName.clicked.connect(self.btnSelectFileName_click)
        self.btnCreateFile.clicked.connect(self.btnCreateFile_click)
        self.btnOpenFile.clicked.connect(self.btnOpenFile_click)
        self.btnLogin.clicked.connect(self.btnLogin_click)

        self.btnSave.clicked.connect(self.btnSave_click)
        self.btnCancel.clicked.connect(self.btnCancel_click)

        self.btnGenerate.clicked.connect(self.btnGenerate_click)
        self.btnCloseFile.clicked.connect(self.btnCloseFile_click)

        self.btnCreate.clicked.connect(self.recordCreate_action)
        self.btnEdit.clicked.connect(self.recordEdit_action)
        self.btnRemove.clicked.connect(self.recordRemove_action)
        self.action_CreateRecord.triggered.connect(self.recordCreate_action)
        self.action_EditRecord.triggered.connect(self.recordEdit_action)
        self.action_RemoveRecord.triggered.connect(self.recordRemove_action)
        self.action_Exit.triggered.connect(lambda x: self.close())
        self.action_MasterPassword.triggered.connect(self.showMasterPassword)

        self.action_PasswordGenerator.triggered.connect(self.showPasswordGeneretor)
        self.action_Block.triggered.connect(self.block)

        self.listWidget.itemSelectionChanged.connect(self.listWidget_onSelect)

        self.listWidget_onSelect()
        self.__update_status_bar()

    def showPasswordGeneretor(self):
        self.__password_generator.exec_()

    def showMasterPassword(self):
        masterPasswordForm = MasterPassword()
        masterPasswordForm.exec_()
        if masterPasswordForm.master_password:
            self.__master_password = masterPasswordForm.master_password
            self.__save()

    def block(self):
        self.__page_id = 0
        self.__master_password = None
        self.__password_uuid = None
        self.__set_edit_mode(False)
        self.action_Block.setEnabled(False)
        self.action_MasterPassword.setEnabled(False)
        self.action_CreateRecord.setEnabled(False)
        self.action_EditRecord.setEnabled(False)
        self.action_RemoveRecord.setEnabled(False)

        self.stackedWidget.setCurrentIndex(self.__page_id)
        self.editMasterPassword.setText("")

    def btnCloseFile_click(self):
        self.__page_id = 1
        self.__settings.file_name = ""
        self.stackedWidget.setCurrentIndex(self.__page_id)
        self.__update_status_bar()

    def listWidget_onSelect(self):
        self.__password_uuid = None

        if self.listWidget.selectedItems():
            self.__password_uuid = self.listWidget.selectedItems()[0].data(QtCore.Qt.UserRole + 1)

            password = self.__passwords[self.__password_uuid]
            self.editTitle.setText(password.title)
            self.editLogin.setText(password.login)
            self.editPassword.setText(password.password)
            self.editSite.setText(password.site)
            self.textEditAdditional.setPlainText(password.additional)

        self.action_CreateRecord.setEnabled(not self.__edit_mode and self.__page_id == 2)
        self.action_EditRecord.setEnabled(self.__password_uuid is not None)
        self.action_RemoveRecord.setEnabled(self.__password_uuid is not None)
        self.btnCreate.setEnabled(not self.__edit_mode)
        self.btnEdit.setEnabled(self.__password_uuid is not None)
        self.btnRemove.setEnabled(self.__password_uuid is not None)

    def recordRemove_action(self):
        if self.__password_uuid:
            del self.__passwords[self.__password_uuid]
            self.__save()
            self.__update_listWidget()

            self.__password_uuid = None
            self.__clear()

    def recordCreate_action(self):
        self.__password_uuid = None
        self.__set_edit_mode()
        self.__clear()

    def recordEdit_action(self):
        self.__set_edit_mode()

    def btnGenerate_click(self):
        self.editPassword.setText(self.__password_generator.generate())

    def btnSave_click(self):
        if not self.editTitle.text():
            show_message("Введите Название")
            return

        if not self.editLogin.text():
            show_message("Введите Логин")
            return

        if not self.editPassword.text():
            show_message("Введите Пароль")
            return

        if self.__password_uuid is None:
            self.__password_uuid = self.__add_password().uuid
        else:
            password = self.__passwords[self.__password_uuid]
            password.title = self.editTitle.text()
            password.login = self.editLogin.text()
            password.password = self.editPassword.text()
            password.site = self.editSite.text()
            password.additional = self.textEditAdditional.toPlainText()

            self.__save()

        self.__set_edit_mode(False)

    def btnCancel_click(self):
        self.__set_edit_mode(False)
        self.__clear()
        self.__update_listWidget()

    def btnOpenFile_click(self):
        file_name = QFileDialog.getOpenFileName(self,
                                                caption="Выберите файл хранилища",
                                                filter="Файл хранилища (*.data)")[0]
        if file_name:
            self.__settings.file_name = file_name

            self.__page_id = 0
            self.stackedWidget.setCurrentIndex(self.__page_id)
            self.__update_status_bar()

    def btnSelectFileName_click(self):
        file_name = QFileDialog.getSaveFileName(self,
                                                caption="Выберите имя файла",
                                                filter="Файл хранилища (*.data)")[0]
        if file_name:
            self.editFileName.setText(file_name)

    def btnCreateFile_click(self):
        if not self.editFileName.text():
            show_message("Выберите имя файла")
            return

        if not self.editCreateMasterPassword.text():
            show_message("Выберите пароль")
            return

        if len(self.editCreateMasterPassword.text()) < self.__settings.min_length:
            show_message(f"Минимальная длина пароля {self.__settings.min_length} символов")
            return

        if self.editCreateMasterPassword.text() != self.editConfirmMasterPassword.text():
            show_message("Пароли не совпадают")
            return

        self.__master_password = self.editCreateMasterPassword.text()
        self.__settings.file_name = self.editFileName.text()
        self.__save()

        self.__page_id = 2
        self.stackedWidget.setCurrentIndex(self.__page_id)

    def btnLogin_click(self):
        self.__master_password = self.editMasterPassword.text()
        if not self.__load():
            return

        self.__update_listWidget()
        self.__set_edit_mode(False)
        self.__page_id = 2
        self.stackedWidget.setCurrentIndex(self.__page_id)
        self.action_MasterPassword.setEnabled(True)
        self.action_Block.setEnabled(True)

    def __update_listWidget(self):
        self.listWidget.clear()
        for key in self.__passwords:
            password = self.__passwords[key]
            li = QListWidgetItem(f"{password.title.upper()}\n{password.login}")
            li.setData(QtCore.Qt.UserRole + 1, password.uuid)
            self.listWidget.addItem(li)

    def __add_password(self):
        password = Password(title=self.editTitle.text(),
                            login=self.editLogin.text(),
                            password=self.editPassword.text(),
                            site=self.editSite.text(),
                            additional=self.textEditAdditional.toPlainText())

        self.__passwords[password.uuid] = password
        self.__save()
        self.__update_listWidget()

        return password

    def __load(self) -> bool:
        cf = CryptoFile(self.__settings.file_name)

        try:
            data = json.loads(cf.load(self.__master_password))
        except InvalidPasswordException:
            show_message("Неверный пароль")
            return False
        except InvalidFormatException:
            show_message("Неверный формат файла")
            return False

        for key in data["passwords"]:
            self.__passwords[key] = Password.from_json(data["passwords"][key])

        for key in data["notepad"]:
            self.__pages[key] = Page.from_json(data["notepad"][key])

        return True

    def __save(self) -> None:
        data = {
            "passwords": self.__passwords,
            "notepad": self.__pages,
        }

        cf = CryptoFile(self.__settings.file_name)
        cf.save(json.dumps(data, ensure_ascii=False, cls=ClassEncoder), self.__master_password)

    def __set_edit_mode(self, edit_mode: bool = True):
        self.__edit_mode = edit_mode

        self.btnCreate.setVisible(not edit_mode)
        self.btnSave.setVisible(edit_mode)
        self.btnCancel.setVisible(edit_mode)
        self.btnEdit.setVisible(not edit_mode)
        self.btnRemove.setVisible(not edit_mode)

        self.editTitle.setReadOnly(not edit_mode)
        self.editLogin.setReadOnly(not edit_mode)
        self.editPassword.setReadOnly(not edit_mode)
        self.editSite.setReadOnly(not edit_mode)
        self.textEditAdditional.setReadOnly(not edit_mode)

        self.btnGenerate.setEnabled(edit_mode)
        self.action_CreateRecord.setEnabled(not self.__edit_mode)

        self.__update_status_bar()

    def __clear(self):
        self.editTitle.setText("")
        self.editLogin.setText("")
        self.editPassword.setText("")
        self.editSite.setText("")
        self.textEditAdditional.setText("")

    def __update_status_bar(self):
        msg = list()
        if self.__settings.file_name:
            msg.append(f"Файл: {self.__settings.file_name}")
        if self.__edit_mode:
            msg.append("Режим редактирования")

        self.statusbar.showMessage(" | ".join(msg))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('windowsvista')

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
