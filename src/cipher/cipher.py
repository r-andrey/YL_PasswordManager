"""
cipher.py

andrey.rudin@gmail.com
"""

from enum import Enum


class CipherMode(Enum):
    """
    Класс перечисляет доступные режимы шифрования
    """

    ECB = 0
    """ Электронная кодовая книга """

    CFB = 1
    """ Обратная связь по шифротексту """


class Operation(Enum):
    """
    Класс перечисляет методы работы
    """

    ENCRYPTION = 0
    """ Шифрование """

    DECRYPTION = 1
    """ Дешифрование """


class BaseCipher(object):
    """
    Базовый шифровальщик. Абстрактный класс
    """

    def __init__(self):

        # Режми шифрования (по умолчанию ECB)
        self.__mode = CipherMode.ECB

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self, value: CipherMode):
        self.__mode = value

    def _process_data_ECB(self, data: bytearray, operation: Operation) -> None:
        """ Шифрование / дешифрование с применением режима электронной кодовой книги """
        pass

    def _process_data_CFB(self, data: bytearray, operation: Operation) -> None:
        """ Шифрование / дешифрование с применением режима обратной связи по шифротексту """
        pass

    def set_key(self, key: bytes) -> None:
        """ Установка ключа шифрования """
        pass

    def encrypt(self, data: bytearray) -> None:
        """ Шифрование данных """

        if self.__mode == CipherMode.ECB:
            self._process_data_ECB(data, operation=Operation.ENCRYPTION)
        if self.__mode == CipherMode.CFB:
            self._process_data_CFB(data, operation=Operation.ENCRYPTION)

    def decrypt(self, data: bytearray) -> None:
        """ Дешифрование данных """

        if self.__mode == CipherMode.ECB:
            self._process_data_ECB(data, operation=Operation.DECRYPTION)
        if self.__mode == CipherMode.CFB:
            self._process_data_CFB(data, operation=Operation.DECRYPTION)
