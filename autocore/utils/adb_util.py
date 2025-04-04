import base64
import re
import socket
import time
from datetime import datetime

import pkg_resources
from getgauge.python import data_store
from ppadb.client import Client as AdbClient

from . import logger

# from .API_request import APIRequest


class ADBUtil:
    client: AdbClient
    device: AdbClient.device

    def __init__(self, udid='emulator-5554', host='127.0.0.1', port=5037):
        self.client = AdbClient(host=host, port=port)
        self.device = self.connect_to_device(udid)

    def connect_to_device(self, udid):
        try:
            return self.client.device(udid)
        except Exception as exception:
            logger.error(exception)

    # ==================================================
    # Call package manager (pm)
    # ==================================================

    def _call_package_manager(self, command: str):
        """
        Within an adb shell, you can issue commands with the package manager (pm) tool to perform actions and queries on app packages installed on the device.
        """
        try:
            return self.device.shell(f'pm {command}')
        except Exception as exception:
            logger.error(exception)

    def clear_data(self, package: str):
        """
        Deletes all data associated with a package.
        """
        try:
            command = f'clear {package}'
            return self._call_package_manager(command)
        except Exception as exception:
            logger.error(exception)