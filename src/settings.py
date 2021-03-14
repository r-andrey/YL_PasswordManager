"""
settings.py

andrey.rudin@gmail.com
"""

from configparser import ConfigParser
from os.path import exists


class Settings:
    """
    Класс реализует логику работы с настройками программы
    """
    def __init__(self):
        self.__config_file_name = "settings.ini"

        if not exists(self.__config_file_name):
            with open(self.__config_file_name, "w") as f:
                f.write("[file]\n[master_password]\n[password_generator]\n")
                f.close()

        self.__config = ConfigParser()
        self.__config.read(self.__config_file_name)

        self.title = "Менеджер паролей"
        self.version = 1.0

    def __store(self):
        with open(self.__config_file_name, 'w') as f:
            self.__config.write(f)

    @property
    def file_name(self) -> str:
        return self.__config.get("file", "file_name", fallback=None)

    @file_name.setter
    def file_name(self, value: str) -> None:
        self.__config.set("file", "file_name", value)
        self.__store()

    @property
    def min_length(self) -> int:
        return int(self.__config.get("master_password", "min_length", fallback=8))

    @min_length.setter
    def min_length(self, value: int) -> None:
        self.__config.set("master_password", "min_length", str(value))
        self.__store()

    @property
    def password_len(self) -> int:
        return int(self.__config.get("password_generator", "password_len", fallback=8))

    @password_len.setter
    def password_len(self, value: int) -> None:
        self.__config.set("password_generator", "password_len", str(value))
        self.__store()

    @property
    def lat1(self) -> bool:
        return bool(self.__config.get("password_generator", "lat1", fallback=True))

    @lat1.setter
    def lat1(self, value: bool) -> None:
        self.__config.set("password_generator", "lat1", str(value))
        self.__store()

    @property
    def lat2(self) -> bool:
        return bool(self.__config.get("password_generator", "lat2", fallback=False))

    @lat2.setter
    def lat2(self, value: bool) -> None:
        self.__config.set("password_generator", "lat2", str(value))
        self.__store()

    @property
    def numbers(self) -> bool:
        return bool(self.__config.get("password_generator", "numbers", fallback=False))

    @numbers.setter
    def numbers(self, value: bool) -> None:
        self.__config.set("password_generator", "numbers", str(value))
        self.__store()

    @property
    def special(self) -> bool:
        return bool(self.__config.get("password_generator", "special", fallback=False))

    @special.setter
    def special(self, value: bool) -> None:
        self.__config.set("password_generator", "special", str(value))
        self.__store()

    @property
    def ambiguous(self) -> bool:
        return bool(self.__config.get("password_generator", "ambiguous", fallback=True))

    @ambiguous.setter
    def ambiguous(self, value: bool) -> None:
        self.__config.set("password_generator", "ambiguous", str(value))
        self.__store()
