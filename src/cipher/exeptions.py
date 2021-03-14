"""
exceptions.py

andrey.rudin@gmail.com
"""


class KeySizeException(Exception):
    """
    Исключение: неверный размер ключа шифрования
    """
    pass


class BlockSizeException(Exception):
    """
    Исключение: неверный размер блока данных
    """
    pass


class IVSizeException(Exception):
    """
    Исключение: неверный размер вектора инициализации
    """
    pass
