"""
gost.py

andrey.rudin@gmail.com
"""

from . exeptions import BlockSizeException, KeySizeException, IVSizeException
from . cipher import BaseCipher, Operation


class GostCipher(BaseCipher):
    """
    Класс реализует шифрование / дешифрование данных при помощи
    алгоритма ГОСТ 28147-89
    """

    def __init__(self):

        super().__init__()

        # Вектор инициализации
        self.__iv = bytes.fromhex("01 23 45 67 89 AB CD EF")

        # S-блок (id-tc26-gost-28147-param-Z)
        self.__s_block = (
            (12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1),
            (6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15),
            (11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0),
            (12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11),
            (7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12),
            (5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0),
            (8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7),
            (1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2)
        )

        self.__keys = list()
        self.set_key(bytes(32))

    def set_key(self, key: bytes) -> None:
        """ Установка ключа шифрования """

        if len(key) != 32:
            raise KeySizeException

        # Генерация раундовых ключей шифрования
        self.__keys = list()
        for i in range(32):
            idx = i % 8 if i < 24 else 7 - i % 8
            self.__keys.append(int.from_bytes(key[idx * 4:idx * 4 + 4], byteorder='big', signed=False))

    def set_iv(self, iv: bytes) -> None:
        """ Установка вектора инициализации """

        if len(iv) != 8:
            raise IVSizeException

        self.__iv = iv

    def __process_block(self, block: bytes, operation: Operation) -> bytes:
        """ Шифрование / дешифрование одного блока данных"""

        if len(block) != 8:
            raise BlockSizeException

        # a - старшая половина блока, b - младшая
        a = int.from_bytes(block[0:4], byteorder='big', signed=False)
        b = int.from_bytes(block[4:8], byteorder='big', signed=False)

        for r in range(32):
            # Получение раундового ключа шифрования.
            # При операции дешифрования ключи беруться в обратной последовательности
            key = self.__keys[r] if operation == Operation.ENCRYPTION else self.__keys[31 - r]

            s = (b + key) & 0xFFFFFFFF

            t = 0
            for i in range(8):
                t |= self.__s_block[i][s >> (4 * i) & 0x0F] << (4 * i)

            s = ((t >> (32 - 11)) | (t << 11)) & 0xFFFFFFFF

            s ^= a

            # В последнем раунде перестановка старшей и младшей части блока не производится
            if r == 31:
                a = s
            else:
                a, b = b, s

        return a.to_bytes(4, byteorder='big', signed=False) + b.to_bytes(4, byteorder='big', signed=False)

    def _process_data_CFB(self, data: bytearray, operation: Operation) -> None:
        """ Шифрование / дешифрование с применением режима обратной связи по шифротексту """

        # Синхропосылка
        s = self.__iv

        seek = 0
        while seek < len(data):
            t = self.__process_block(s, operation=Operation.ENCRYPTION)

            if operation == Operation.DECRYPTION:
                s = data[seek:seek + 8]

            for i in range(8):
                if seek + i < len(data):
                    data[seek + i] ^= t[i]
                else:
                    break

            if operation == Operation.ENCRYPTION:
                s = data[seek:seek + 8]

            seek += 8

    def _process_data_ECB(self, data: bytearray, operation: Operation) -> None:
        """ Шифрование / дешифрование с применением режима электронной кодовой книги """

        # Размер данных должен быть кратен 8 байтам (64 битам)
        if len(data) % 8 != 0:
            data += bytearray(8 - len(data) % 8)

        seek = 0
        while seek < len(data):
            block = data[seek:seek + 8]

            block = self.__process_block(block, operation)
            for i in range(8):
                data[seek + i] = block[i]

            seek += 8
