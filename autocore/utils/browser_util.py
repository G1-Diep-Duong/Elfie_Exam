import contextlib
import datetime
import os
import platform
import random
import re
import socket

# import subprocess
import time
from pathlib import Path

import psutil
import toml
from appium import webdriver as AppiumWebDriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.appium_service import AppiumService
from get_chrome_driver import GetChromeDriver
from getgauge.python import Messages, data_store
from getgauge.util import get_project_root
from isim import Device as iOS_Device
from screeninfo import get_monitors
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.core.utils import read_version_from_cmd

from . import gauge_wrap, logger, timing
from .API_request import APIRequest
from .string_util import StringUtil


class ChromeType(object):
    GOOGLE = "google-chrome"
    CHROMIUM = "chromium"
    BRAVE = "brave-browser"
    MSEDGE = "edge"


PROJECT_PATH = get_project_root()
WDAR = "/WebDriverAgentRunner-Runner.app"
LOCALHOST = socket.gethostbyname("localhost")
PATTERN = {
    ChromeType.CHROMIUM: r"\d+\.\d+\.\d+",
    ChromeType.GOOGLE: r"\d+\.\d+\.\d+(\.\d+)?",
    ChromeType.MSEDGE: r"\d+\.\d+\.\d+",
    "brave-browser": r"\d+\.\d+\.\d+(\.\d+)?",
    "firefox": r"(\d+.\d+)",
}


class BrowserUtil:
    @staticmethod
    def create_chrome_driver(download_directory=os.path.join(PROJECT_PATH, "download"), user_profile_dir: str = None, chrome_options=None):
        chrome_service = None
        driver = None
        try:
            if hasattr(data_store, "chrome_opts"):
                chrome_options = data_store.chrome_opts
            elif chrome_options is None:
                chrome_options = get_default_chrome_options(download_directory)

            if user_profile_dir is not None:
                chrome_options.add_argument(f"user-data-dir={user_profile_dir}")

            chrome_options.page_load_strategy = "none"
            chrome_options.accept_insecure_certs = True
            chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
            chrome_options.add_experimental_option(
                "perfLoggingPrefs",
                {
                    "enableNetwork": True,
                    "enablePage": False,
                },
            )

            try:
                if len(chrome_options.binary_location) == 0:
                    chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                chrome_cmd = f"'{chrome_options.binary_location}' --version"
                actual_version = read_version_from_cmd(chrome_cmd, PATTERN["google-chrome"])
                chrome_service = ChromeService(executable_path=get_specific_related_chrome_version(actual_version.split(".")[0].strip()))
            except Exception as exception:
                logger.warning(exception)

            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

            if driver is not None:
                driver.set_page_load_timeout(30)
                try:
                    if chrome_options._caps.get("goog:chromeOptions") is not None and chrome_options._caps["goog:chromeOptions"].get("prefs") is not None and chrome_options._caps["goog:chromeOptions"]["prefs"].get("download.default_directory") is not None:
                        driver.__dict__.update({"download_directory": chrome_options._caps["goog:chromeOptions"]["prefs"]["download.default_directory"]})
                except Exception as exception:
                    logger.warning(exception)
                BrowserUtil.set_window_size_based_on_monitor_resolution(driver)
            return driver
        except Exception as exception:
            logger.error(exception)

    @staticmethod
    def create_android_driver(desired_capabilities=None):
        udid = data_store.suite.mobile_udid
        if hasattr(data_store.suite, "repeat_creating_android_driver") and len(data_store.suite["repeat_creating_android_driver"]) > 0:
            return None

        # connected_devices = BrowserUtil.get_connected_devices_android()
        # if len(connected_devices) == 0:
        #     message = "Cannot create Mobile Driver - Please check devices are connected or not ... !!!"
        #     logger.warning(message)
        #     if data_store.suite.license:
        #         Messages.write_message(message)
        #     return None
        # driver = None

        # if data_store.suite.mobile_udid is None:
        #     udid = BrowserUtil.get_available_device_android()
        # else:
        #     udid = data_store.suite.mobile_udid

        if udid is None:
            message = "Not enough devices for testing - Please check it again !!!"
            logger.warning(message)
            if data_store.suite.license:
                Messages.write_message(message)
            return None

        # if udid not in connected_devices:
        #     message = f"Device {udid} was not in the list of connected devices !!!"
        #     logger.warning(message)
        #     if data_store.suite.license:
        #         Messages.write_message(message)
        #     return None

        # if udid in BrowserUtil.get_busy_devices():
        #     message = f"Device ({udid}) is under testing or stuck - Please check stuck devices if any ... !!!"
        #     logger.warning(message)
        #     if data_store.suite.license:
        #         Messages.write_message(message)
        #     data_store.suite["repeat_creating_android_driver"] = False
        #     return None

        if hasattr(data_store, "mobile_caps") and len(data_store.mobile_caps) > 0:
            desired_capabilities = data_store.mobile_caps

        if desired_capabilities is None and udid is not None:
            caps = {
                "platformName": "Android",
                "appium:deviceName": f"Android {udid}",
                "appium:automationName": "UiAutomator2",
                "appium:udid": udid,
                "appium:ensureWebviewsHavePages": True,
                "appium:nativeWebScreenshot": True,
                "appium:newCommandTimeout": 3600,
                "appium:autoGrantPermissions": True,
                "unicodeKeyboard": True,
            }
        else:
            caps = desired_capabilities
            if "appium:udid" not in caps:
                caps["appium:udid"] = udid
        
        try:
            if udid is not None:
                if hasattr(data_store.suite, "appium_service_port"):
                    port = data_store.suite.appium_service_port
                else:
                    port = BrowserUtil.start_appium_service()

                if caps is not None and port is not None:
                    driver = AppiumWebDriver.Remote(
                        command_executor=f"http://{LOCALHOST}:{port}/wd/hub",
                        options=UiAutomator2Options().load_capabilities(caps),
                    )

                if driver is not None:
                    logger.debug(f"Device {driver.caps['deviceModel']} ({udid}) is under testing ... !!!")
                    return driver
            if driver is None:
                message = "Not enough devices to run - Please check stuck devices if any ... !!!"
                logger.warning(message)
                if data_store.suite.license:
                    Messages.write_message(message)
                return None
        except Exception as exception:
            logger.error(exception)
            if driver is not None:
                driver.quit()
            return None

    @staticmethod
    def create_ios_driver(desired_capabilities=None) -> AppiumWebDriver:
        if hasattr(data_store.suite, "repeat_creating_ios_driver") and len(data_store.suite["repeat_creating_ios_driver"]) > 0:
            return None

        device_name = None
        ios_simulator = None
        data_store.suite.ios_simulator_device = False
        udid = data_store.suite.mobile_udid
        driver = None

        with contextlib.suppress(Exception):
            ios_simulator = iOS_Device.from_identifier(udid)

        if ios_simulator:
            data_store.suite.ios_simulator_device = True
            for item in get_ios_devices():
                if udid.strip() in item:
                    data_store.suite.mobile_platform_version = item.split(f"({udid})")[0].split("(")[-1:][0].split(")")[0]
            device_name = ios_simulator.name
            if udid in BrowserUtil.get_busy_devices():
                message = f"Device {device_name} ({udid}) is under testing or stuck - Please check stuck devices if any ... !!!"
                logger.warning(message)
                if data_store.suite.license:
                    Messages.write_message(message)
                data_store.suite["repeat_creating_ios_driver"] = False
                return None

            for _ in range(10):
                ios_simulator.refresh_state()
                if ios_simulator.state.lower() != "booted":
                    ios_simulator.boot()
                else:
                    break

            if ios_simulator.state.lower() != "booted":
                message = f"Device {device_name} ({udid}) has not been booted ... !!!"
                logger.warning(message)
                if data_store.suite.license:
                    Messages.write_message(message)
                return None

        else:
            for item in get_ios_devices():
                if udid.strip() in item:
                    data_store.suite.mobile_platform_version = item.split(f"({udid})")[0].split("(")[-1:][0].split(")")[0]
                    device_name = item.split(f"({udid})")[0].split(f"({data_store.suite.mobile_platform_version})")[0].strip()

        # ==========================================================================================

        if hasattr(data_store, "mobile_caps") and len(data_store.mobile_caps) > 0:
            desired_capabilities = data_store.mobile_caps

        if desired_capabilities is None and udid is not None:
            wdaLocalPort = get_free_port()
            caps = {
                "platformName": "iOS",
                "appium:platformVersion": f"{data_store.suite.mobile_platform_version}",
                "appium:deviceName": f"{device_name}",
                "appium:automationName": "XCUITest",
                "appium:udid": udid,
                "appium:newCommandTimeout": 3600,
                "appium:autoGrantPermissions": True,
                "appium:includeSafariInWebviews": True,
                "unicodeKeyboard": True,
                "locationServicesEnabled": True,
                "locationServicesAuthorized": True,
                "appium:wdaLocalPort": wdaLocalPort,
            }
        else:
            caps = desired_capabilities

        try:
            if udid is not None:
                if hasattr(data_store.suite, "appium_service_port"):
                    port = data_store.suite.appium_service_port
                else:
                    port = BrowserUtil.start_appium_service()

                if caps is not None and port is not None:
                    driver = AppiumWebDriver.Remote(
                        command_executor=f"http://{LOCALHOST}:{port}/wd/hub",
                        options=XCUITestOptions().load_capabilities(caps),
                    )

                if driver is not None:
                    logger.debug(f"Device {driver.caps['deviceName']} ({udid}) is under testing ... !!!")
                    return driver
            if driver is None:
                return None
        except Exception as exception:
            if "xcodebuild failed with code 65" not in str(exception):
                logger.error(exception)
            if hasattr(data_store.suite, "appium_service"):
                data_store.suite.appium_service.stop()
            if driver is not None:
                driver.quit()
            return None

    @staticmethod
    def set_window_size_based_on_monitor_resolution(driver):
        try:
            # if platform.system() == "Darwin":
            #     driver.set_window_size(7680, 4320)
            #     driver.set_window_position(0, 0)
            # default_window_position_x = driver.get_window_position()["x"]
            # default_window_position_y = driver.get_window_position()["y"]

            driver.maximize_window()
            default_window_width = driver.get_window_size()["width"]
            default_window_height = driver.get_window_size()["height"]
            new_window_width = default_window_height * 16 / 9 if default_window_width / default_window_height > 17 / 9 else default_window_width
            # driver.set_window_position(default_window_position_x, default_window_position_y)

            if new_window_width != default_window_width:
                driver.set_window_size(new_window_width, default_window_height)

        except Exception as exception:
            logger.error(exception)

    @staticmethod
    def close_all_browser_tabs(driver: WebDriver):
        try:
            dwh = driver.window_handles
            for tab in dwh:
                driver.switch_to.window(tab)
                driver.close()
        except Exception as exception:
            logger.error(exception)

    @staticmethod
    def close_all_redundant_tabs(driver: WebDriver):
        try:
            if len(driver.window_handles) > 1:
                for window_handle in driver.window_handles[:-1]:
                    driver.switch_to.window(window_handle)
                    driver.close()
            driver.switch_to.window(driver.window_handles[-1])
        except Exception as exception:
            if exception.__dict__.get("msg"):
                message = exception.__dict__.get("msg")
                logger.warning(message)
                if data_store.suite.license:
                    Messages.write_message(message)
            else:
                logger.error(exception)

    @staticmethod
    def reset_driver(driver: WebDriver):
        try:
            driver.delete_all_cookies()
            BrowserUtil.close_all_redundant_tabs(driver)
            driver.refresh()
        except Exception as exception:
            if exception.__dict__.get("msg"):
                message = exception.__dict__.get("msg")
                logger.warning(message)
                if data_store.suite.license:
                    Messages.write_message(message)
            else:
                logger.error(exception)

    @staticmethod
    def start_appium_service():
        try:
            if hasattr(data_store.suite, "appium_service"):
                data_store.suite.appium_service.stop()
            appium_service = AppiumService()

            for _ in range(10):
                port = get_free_port()
                appium_service.start(args=["-p", str(port), "-pa", "/wd/hub", "--allow-insecure=get_server_logs"])
                if appium_service.is_running and appium_service.is_listening:
                    data_store.suite.appium_service = appium_service
                    # logger.debug("Appium Server has started ... !!!")
                    return port
        except Exception as exception:
            logger.warning(exception)
            if data_store.suite.license:
                Messages.write_message(exception)
            if hasattr(data_store.suite, "appium_service"):
                data_store.suite.appium_service.stop()

            return None

    # @staticmethod
    # def get_connected_devices_android():
    #     try:
    #         import subprocess
    #         devices = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True).stdout.splitlines()
    #         # devices = os.popen("adb devices").readlines()
    #         return [device.split("\t")[0] for device in devices if "\tdevice" in device]
    #     except Exception as exception:
    #         logger.warning(exception)
    #         if data_store.suite.license:
    #             Messages.write_message(exception)

    # @staticmethod
    # def get_available_device_android():
    #     try:
    #         connected_devices = BrowserUtil.get_connected_devices_android()
    #         busy_devices = BrowserUtil.get_busy_devices()
    #         for device in connected_devices:
    #             if device not in busy_devices:
    #                 return device
    #     except Exception as exception:
    #         logger.warning(exception)
    #         if data_store.suite.license:
    #             Messages.write_message(exception)
    #         return None

    # @staticmethod
    # def get_busy_devices():
    #     try:
    #         result = []
    #         for proc in psutil.process_iter():
    #             if proc.status() == "running" and proc.name() in [
    #                 "node",
    #                 "node.exe",
    #             ]:
    #                 cmd = proc.cmdline()
    #                 if "/wd/hub" in cmd:
    #                     for arg in cmd:
    #                         if arg in ["-p"]:
    #                             port = cmd[cmd.index(arg) + 1]
    #                             udid = BrowserUtil.get_udid_from_port(port)
    #                             if udid:
    #                                 result.append(udid)
    #         return result
    #     except Exception as exception:
    #         logger.error(exception)
    #         return []

    @staticmethod
    def get_udid_from_port(port):
        try:
            api = APIRequest()
            result = api.get(f"http://{LOCALHOST}:{port}/wd/hub/sessions")
            if result is not None:
                return None if len(result.json.get("value")) == 0 else result.json.get("value")[0].get("capabilities").get("udid")
        except Exception as exception:
            logger.error(exception)
            return None


# ===============================================================================================


class ChromeOpts:
    _chrome_options: webdriver.ChromeOptions

    def __init__(self, chrome_options=None):
        self._chrome_options = get_default_chrome_options() if chrome_options is None else chrome_options
        self._chrome_options.page_load_strategy = "none"
        self._chrome_options.accept_insecure_certs = True
        data_store.chrome_opts = self._chrome_options


class MobileCapabilities:
    _capabilities: dict

    def __init__(self, capabilities_dict=None):
        self._capabilities = {} if capabilities_dict is None else capabilities_dict
        data_store.mobile_caps = self._capabilities


# ===============================================================================================


def enable_download_in_headless_chrome(driver, download_dir):
    # add missing support for chrome "send_command"  to selenium webdriver
    driver.command_executor._commands["send_command"] = (
        "POST",
        "/session/$sessionId/chromium/send_command",
    )
    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {"behavior": "allow", "downloadPath": download_dir},
    }
    driver.execute("send_command", params)


def get_default_chrome_options(download_directory=os.path.join(PROJECT_PATH, "download")):
    # sourcery skip: extract-method
    try:
        if platform.system() != "Windows":
            for monitor in get_monitors():
                x = monitor.x
                y = monitor.y * -1
                if monitor.is_primary is False:
                    break
        else:
            x = 0
            y = 0
    except Exception as exception:
        logger.error(exception)
        x = 0
        y = 0

    try:
        # https://peter.sh/experiments/chromium-command-line-switches/
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f"--window-position={x},{y}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--proxy-auto-detect")
        chrome_options.add_argument("--allow-insecure-localhost")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--enable-auto-reload")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--enable-javascript")
        # chrome_options.add_argument("--window-size=1920,1080")
        # chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument('--disable-logging')
        # chrome_options.add_argument("--disable-notifications")
        # chrome_options.add_argument("--force-dark-mode")
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        prefs = {
            "credentials_enable_service": False,
            "download.default_directory": download_directory,
            "download.directory_upgrade": True,
            "download.prompt_for_download": False,
            "profile.default_content_setting_values.geolocation": 1,
            "profile.default_content_setting_values.notifications": 1,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        return chrome_options
    except Exception as exception:
        logger.error(exception)
        return webdriver.ChromeOptions()


def get_free_port(host=LOCALHOST):
    try:
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.bind((host, 0))
        # port = sock.getsockname()[1]
        # sock.close()
        # return port

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, 0))
            return sock.getsockname()[1]
    except Exception as exception:
        logger.error(exception)


# def ios_install_WDAR(udid):
#     try:
#         wdarp = ios_find_WDAR_app()
#         if wdarp:
#             for _ in range(3):
#                 if data_store.suite.ios_simulator_device:
#                     os.popen(f"xcrun simctl install {udid} {wdarp}")
#                     for _ in range(10):
#                         with contextlib.suppress(Exception):
#                             if get_WDAR_identifier(udid) is not None:
#                                 return True
#         else:
#             message = "WDA Runner is not available for installing !!!"
#             logger.warning(message)
#             if data_store.suite.license:
#                 Messages.write_message(message)
#         return False
#     except Exception as exception:
#         logger.error(exception)
#         return False


# def ios_find_WDAR_app():
#     try:
#         return next(
#             (path[: path.find(WDAR) + len(WDAR)] for path, subdirs, files in os.walk("/Users") if WDAR in path),
#             None,
#         )
#     except Exception as exception:
#         logger.error(exception)


def get_specific_related_chrome_version(version):
    try:
        related_version = None
        api = APIRequest()

        if int(version) <= 114:
            content = api.get("https://chromedriver.storage.googleapis.com/")
            result = re.findall("<Key>(.+?)</Key>", content.text)
            for item in result:
                if "/notes.txt" in item and item.strip().startswith(f"{version}."):
                    related_version = item.split("/notes.txt")[0]
        else:
            content = api.get("https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json")
            result = re.findall('version":"(.+?)","revision', content.text)
            for item in result:
                if item.startswith(f"{version}."):
                    related_version = item

        if related_version is not None:
            download_directory = os.path.join(Path(PROJECT_PATH).parent.absolute(), "ChromeDriver", related_version)
            expected_chrome_driver = os.path.join(download_directory, "chromedriver")
            if os.path.exists(expected_chrome_driver):
                return expected_chrome_driver
            return os.path.join(
                GetChromeDriver().download_version(
                    version=related_version,
                    output_path=download_directory,
                    extract=True,
                ),
                "chromedriver",
            )
        else:
            logger.warning(f"There is no chrome driver which has version {version} !!!")
            return None
    except Exception as exception:
        logger.error(exception)
        return None


def get_ios_devices():
    import subprocess
    IOS_REGEX_PATTERN = re.compile(r"^(.+) \((.+)\) \((.+)\)$")
    command = "xcrun xctrace list devices 2>&1"
    devices_string = subprocess.check_output(command, shell=True).decode("utf-8")
    devices_list = re.split(r"\n+", devices_string)

    device_entries = []
    # regex_exit_pattern = re.compile(r"Simulators")
    for device_details in devices_list:
        # if regex_exit_pattern.search(device_details):
        #     break
        device_match = IOS_REGEX_PATTERN.match(device_details)
        if device_match:
            device_entries.append(device_match.string)
    return device_entries
