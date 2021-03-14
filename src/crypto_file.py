"""
crypto_file.py

andrey.rudin@gmail.com
"""

from os.path import exists
from cipher import GostCipher, CipherMode
import hashlib
import secrets


class InvalidFormatException(Exception):
    pass


class InvalidPasswordException(Exception):
    pass


class CryptoFile(object):
    """
    Класс релизует логику ввода / вывода информации в файл

    Формат файла
        ЗАГОЛОВОК - 42 байтов
        ТЕКСТОВЫЕ ДАННЫЕ

    Заголовок
        0..1   - сигнатура 0x50 0x4d (PM)
        2..33  - sha256 hash открытых данных
        34..41 - вектор инициализации. Выбирается как случайный набор 8 байт

    Данные
        данные в формате json, зашифрованные с использованием алгоритма шифрование (например, ГОСТ 28147-89)
    """

    def __init__(self, file_name: str) -> None:
        """
        Конструктор
        :param file_name: имя файла
        """
        self.__file_name = file_name
        self.__signature = bytes.fromhex('50 4d')

    def load(self, password: str) -> str:
        """
        Чтение информации из файла и ее дешифрование
        :param password: пароль шифрования
        :return: расшифрованные данные
        """
        if not exists(self.__file_name):
            raise FileNotFoundError

        f = open(self.__file_name, mode='rb')
        signature = f.read(2)
        f.close()

        if signature != self.__signature:
            raise InvalidFormatException

        with open(self.__file_name, mode='rb') as f:
            cipher = GostCipher()
            cipher.mode = CipherMode.CFB
            cipher.set_key(hashlib.sha3_256(password.encode()).digest())
            f.read(2)
            data_hash = f.read(32)
            cipher.set_iv(f.read(8))
            data = bytearray(f.read())

            cipher.decrypt(data)

            if data_hash != hashlib.sha3_256(data).digest():
                raise InvalidPasswordException

            return data.decode(encoding='UTF-8')

    def save(self, data: str, password: str) -> None:
        """
        Шифрование информации и запись ее в файл
        :param data: отурыте данные
        :param password: пароль шифрования
        """
        iv = secrets.token_bytes(8)

        cipher = GostCipher()
        cipher.mode = CipherMode.CFB
        cipher.set_iv(iv)
        cipher.set_key(hashlib.sha3_256(password.encode()).digest())

        data_bytes = data.encode()
        data_hash = hashlib.sha3_256(data_bytes).digest()

        encrypted_data = bytearray(data_bytes)
        cipher.encrypt(encrypted_data)

        with open(self.__file_name, mode='wb') as f:
            f.write(self.__signature)
            f.write(data_hash)
            f.write(iv)
            f.write(encrypted_data)
