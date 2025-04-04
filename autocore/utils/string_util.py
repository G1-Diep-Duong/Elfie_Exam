import base64
import copy
import os
import random
import string


class StringUtil:
    @staticmethod
    def append_dict(first_dict: dict, second_dict: dict) -> dict:
        return copy.deepcopy(first_dict) | second_dict

    @staticmethod
    def encrypt(input_key: str):
        return base64.b64encode(input_key.encode())

    @staticmethod
    def decrypt(input_key):
        return base64.b64decode(input_key).decode("utf-8")

    @staticmethod
    def random_string(size=8):
        # Random a string with size default is 8 - ex: abcdefgx
        lst = [random.choice(string.ascii_letters + string.digits) for _ in range(size)]
        return "".join(lst)

    @staticmethod
    def random_int(size: int):
        # Random an integer number with a size
        return random.randint(0, size - 1)

    @staticmethod
    def join_path(*args):
        return os.path.join(*args)

    @staticmethod
    def format_string(based_string, *sub_string):
        return based_string % sub_string

    @staticmethod
    def base36encode(number):
        if not isinstance(number, (int)):
            raise TypeError("number must be an integer")
        if number < 0:
            raise ValueError("number must be positive")

        alphabet, base36 = ["0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", ""]

        while number:
            number, i = divmod(number, 36)
            base36 = alphabet[i] + base36

        return base36 or alphabet[0]

    @staticmethod
    def base36decode(number):
        return int(number, 36)
