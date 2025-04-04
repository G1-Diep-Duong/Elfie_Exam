import ast
import base64
import contextlib
import json
import os
import pathlib
import re
import shutil
import time

# import time
import unicodedata
import uuid
from datetime import date, datetime
from io import BytesIO
from os import fdopen, remove
from shutil import copymode, move
from tempfile import mkstemp
from uuid import uuid1

import psutil
import toml
from getgauge.python import ExecutionContext, Messages, Screenshots, after_scenario, after_spec, after_step, after_suite, before_scenario, before_spec, before_step, before_suite, continue_on_failure, custom_screenshot_writer, data_store
from getgauge.util import get_project_root
from PIL import Image
from selenium.webdriver.chrome.webdriver import WebDriver

from .base_page import WebPage, WebPage2, WebPage3
from .base_screen import MobileScreen
from .utils import color_names, gauge_wrap, logger
from .utils.browser_util import BrowserUtil, ChromeOpts
from .utils.string_util import StringUtil

# ==================================================================================================
# Gauge Execution Hooks
# ==================================================================================================
PROJECT_PATH = get_project_root()
GHRP = "GAUGE_HTML_REPORT_THEME_PATH"
data_store.suite.license = True


class BaseHook:
    @staticmethod
    @before_suite
    def before_suite_hook(context: ExecutionContext):
        data_store.suite.capture_element_screenshot_time = time.time()
        data_store.suite.current_loc = None
        data_store.suite.current_log_line = get_current_log_line()
        logger.opt(colors=True).info("<i><fg 206>■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■  START TESTING  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■</fg 206></i>")
        data_store.suite.able_to_run = True
        init_config()

    @staticmethod
    @before_spec
    def before_spec_hook(context: ExecutionContext):
        init_spec_data(context)

    @staticmethod
    @before_scenario
    def before_scenario_hook(context: ExecutionContext):
        pass

    @staticmethod
    @before_step
    def before_step_hook(context: ExecutionContext):
        # sourcery skip: move-assign
        executing_flag = f"{init_step_driver(context)} EXECUTING".strip()
        if data_store.suite.able_to_run:
            step_name = str(context.step.text).replace("<", r"\<")
            logger.opt(colors=True).info(f"\n<fg white><i><cyan>‎     * {step_name}   ...[{executing_flag}]</cyan></i></fg white>")

    @staticmethod
    @after_step
    def after_step_hook(context: ExecutionContext):
        # if not data_store.suite.license and not context.step.is_failing:
        #     Screenshots.capture_screenshot()
        data_store.suite.able_to_run = True

    @staticmethod
    @after_scenario
    def after_scenario_hook(context: ExecutionContext):
        pass

    @staticmethod
    @after_spec
    def after_spec_hook(context: ExecutionContext):
        try:
            clean_up_all_web_drivers()
        except Exception as exception:
            logger.error(exception)

    @staticmethod
    @after_suite
    def after_suite_hook(context: ExecutionContext):
        clean_up_all_web_drivers()
        clean_up_mobile_driver()
        # write_log()
        logger.opt(colors=True).info("<i><fg 206>■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■  END TESTING  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■</fg 206></i>")


# ==================================================================================================
# Supported Methods
# ==================================================================================================
def init_config():  # sourcery skip: extract-method
    init_mobile_platform()
    data_store.suite.capture_element_screenshot = None
    config_report_settings()
    data_store.suite.chrome_options = None


def set_mobile_platform_name(udid):
    data_store.suite.mobile_platform_version = None
    data_store.suite.mobile_platform_name = "android"


def load_config():
    try:
        config_file = os.path.join(PROJECT_PATH, "resources", "config.toml")
        if os.path.exists(config_file):
            data_store.suite.update(toml.load(config_file))
    except Exception as exception:
        logger.error(exception)


def init_chrome_driver(download_folder="web_default", user_profile_dir: str = None, chrome_options=None):
    try:
        chrome_driver = None
        chrome_driver = BrowserUtil.create_chrome_driver(
            download_directory=os.path.join(PROJECT_PATH, "download", download_folder),
            user_profile_dir=user_profile_dir,
            chrome_options=chrome_options,
        )
        if chrome_driver is not None and data_store.suite.license:
            message = f"- Testing on {chrome_driver.caps.get('browserName').capitalize()} {chrome_driver.caps.get('browserVersion')}"
            logger.debug(message)
            Messages.write_message(message)

        return chrome_driver
    except Exception as exception:
        logger.error(exception)
        return None


# sourcery skip: use-named-expression
@gauge_wrap
def init_mobile_driver(desired_capabilities=None):
    try:
        if hasattr(data_store, "mobile_caps") and desired_capabilities is None:
            desired_capabilities = data_store.mobile_caps
            if desired_capabilities.get("platformName"):
                data_store.suite.mobile_platform_name = desired_capabilities.get("platformName").lower()

        mobile_driver = None
        if not hasattr(data_store.suite, "mobile_platform_name") or data_store.suite["mobile_platform_name"] is None:
            return None

        if data_store.suite.mobile_platform_name == "android":
            for attemp in range(3):
                logger.debug(f"Init Android Driver... !!! ({attemp+1}/3)")
                mobile_driver = BrowserUtil.create_android_driver(desired_capabilities=desired_capabilities)
                if mobile_driver is not None:
                    break
        else:
            for attemp in range(3):
                logger.debug(f"Init iOS Driver... !!! ({attemp+1}/3)")
                mobile_driver = BrowserUtil.create_ios_driver(desired_capabilities=desired_capabilities)
                if mobile_driver is not None:
                    break

        if mobile_driver is not None:
            if data_store.suite.license:
                if mobile_driver.caps.get("platformName").lower() == "android":
                    Messages.write_message(f"Testing on {mobile_driver.caps.get('deviceModel')} ({mobile_driver.caps.get('platformName')} {mobile_driver.caps.get('platformVersion')}) ({mobile_driver.caps.get('udid')})")
                else:
                    Messages.write_message(f"Testing on {mobile_driver.caps.get('deviceName')} ({mobile_driver.caps.get('platformName')} {mobile_driver.caps.get('platformVersion')}) ({mobile_driver.caps.get('udid')})")

            return mobile_driver
        else:
            # logger.warning(f"Cannot init {data_store.suite.mobile_platform_name} driver... !!!!")
            data_store.suite.able_to_run = False

        return None
    except Exception as exception:
        logger.error(exception)
        return None


@custom_screenshot_writer
def take_screenshot():
    log_message = True
    tc_id = data_store.spec.test_case_id if "test_case_id" in data_store.spec else None
    if ((time.time() - data_store.suite.capture_element_screenshot_time) < 0.001) and data_store.suite.capture_element_screenshot is not None:
        # ==================================================================================================
        # Capture element screenshot
        # ==================================================================================================
        try:
            image = data_store.suite.capture_element_screenshot.screenshot_as_png
            file_name = os.path.join(
                os.getenv("gauge_screenshots_dir"),
                f"screenshot-{tc_id}-{StringUtil.base36encode(uuid1().int)}.png",
            )
            with open(file_name, "wb") as file:
                file.write(image)
            message = f"Your element screenshot has been saved at: {file_name}"
            logger.debug(message)
            return os.path.basename(file_name)
        except Exception as exception:
            logger.error(exception)
        finally:
            data_store.suite.capture_element_screenshot = None
    else:
        list_image = []
        # ==================================================================================================
        # Capture all pages screenshots
        # ==================================================================================================
        try:
            if hasattr(data_store.suite, "web") and data_store.suite["web"] is not None:
                append_screenshot(data_store.suite["web"], tc_id, list_image)
            if hasattr(data_store.suite, "web2") and data_store.suite["web2"] is not None:
                append_screenshot(data_store.suite["web2"], tc_id, list_image)
            if hasattr(data_store.suite, "web3") and data_store.suite["web3"] is not None:
                append_screenshot(data_store.suite["web3"], tc_id, list_image)
            if hasattr(data_store.suite, "mobile") and data_store.suite["mobile"] is not None:
                append_screenshot(data_store.suite["mobile"], tc_id, list_image)

            if list_image:
                images = [Image.open(x) for x in list_image]
                widths, heights = zip(*(i.size for i in images))
                max_height = max(heights)
                resized_images = [im.resize((int(im.size[0] * max_height / im.size[1]), max_height)) for im in images]

                widths, heights = zip(*(i.size for i in resized_images))
                total_width = sum(widths)
                new_im = Image.new("RGB", (total_width, max_height), (256, 256, 256))
                x_offset = 0
                for im in resized_images:
                    new_im.paste(im, (x_offset, 0))
                    x_offset += im.size[0]
                file_name = os.path.join(
                    os.getenv("gauge_screenshots_dir"),
                    f"screenshot-{tc_id}-{StringUtil.base36encode(uuid1().int)}.png",
                )

                new_im.save(file_name)
                for im in list_image:
                    os.remove(im)
            else:
                new_im = Image.new("RGB", (1, 1), (256, 256, 256))
                file_name = os.path.join(
                    os.getenv("gauge_screenshots_dir"),
                    f"screenshot-{tc_id}-{StringUtil.base36encode(uuid1().int)}.png",
                )
                new_im.save(file_name)
                log_message = False

            new_im.close()
            message = f"Your screenshot has been saved at: {file_name}"
            if log_message:
                logger.debug(message)
            return os.path.basename(file_name)
        except Exception as exception:
            logger.error(exception)


def append_screenshot(driver: WebDriver, tc_id, list_image):
    try:
        if len(g_c_o_s(driver.get_screenshot_as_base64())) == 1:
            return None
        image = driver.get_screenshot_as_png()
        image_file_path = os.path.join(os.getenv("gauge_screenshots_dir"), f"screenshot-{tc_id}-{uuid1().int}.png")
        with open(image_file_path, "wb") as file:
            file.write(image)
        list_image.append(image_file_path)
    except Exception as exception:
        logger.error(exception)


def init_spec_data(context):
    try:
        tc_id = unicodedata.normalize("NFKD", context.specification.name.strip().replace(" ", "_")).encode("ASCII", "ignore").decode()
        data_store.spec.tags = context.specification.tags
        pattern = "^&!%.,[]<>:/\\\"'|?*"
        for character in pattern:
            tc_id = tc_id.replace(character, "")
        data_store.spec.test_case_id = tc_id
        data_store.spec.archived_headers = []
        with open(context.specification.file_name, encoding="utf-8") as data:
            for line in data:
                if line.startswith("$"):
                    key = line.split("$")[1].split("=")[0].strip()
                    value = ast.literal_eval(line.split("=")[1].strip())
                    data_store.spec.update({key: value})
    except Exception as exception:
        logger.error(exception)


def init_step_driver(context):
    try:
        test_type = init_step_testing_type(context)
        if test_type is not None:
            test_type = test_type.lower().strip()
            if "WebPage".lower() == test_type and (not hasattr(data_store.suite, "web") or data_store.suite["web"] is None):
                data_store.suite["web"] = init_chrome_driver(
                    download_folder=os.path.join(
                        "web",
                        str(uuid.uuid4()),
                    )
                )
                WebPage.init(data_store.suite["web"])
            if "WebPage2".lower() == test_type and (not hasattr(data_store.suite, "web2") or data_store.suite["web2"] is None):
                data_store.suite["web2"] = init_chrome_driver(
                    download_folder=os.path.join(
                        "web2",
                        str(uuid.uuid4()),
                    )
                )
                WebPage2.init(data_store.suite["web2"])
            if "WebPage3".lower() == test_type and (not hasattr(data_store.suite, "web3") or data_store.suite["web3"] is None):
                data_store.suite["web3"] = init_chrome_driver(
                    download_folder=os.path.join(
                        "web3",
                        str(uuid.uuid4()),
                    )
                )
                WebPage3.init(data_store.suite["web3"])
            if "MobileScreen".lower() == test_type and (not hasattr(data_store.suite, "mobile") or data_store.suite["mobile"] is None):
                data_store.suite["mobile"] = init_mobile_driver()
                if data_store.suite["mobile"] is not None:
                    MobileScreen.init(data_store.suite["mobile"])
                else:
                    logger.warning("Mobile driver cannot be created, please check it again !!!")
                    data_store.suite.able_to_run = False
        return "API" if test_type is None else test_type.upper().replace("SCREEN", "").replace("PAGE", " ").strip()
    except Exception as exception:
        logger.error(exception)


def clean_up_all_web_drivers():
    try:
        if hasattr(data_store.suite, "web") and data_store.suite["web"] is not None:
            data_store.suite["web"].quit()
            data_store.suite["web"] = None
    except Exception as exception:
        logger.error(exception)

    try:
        if hasattr(data_store.suite, "web2") and data_store.suite["web2"] is not None:
            data_store.suite["web2"].quit()
            data_store.suite["web2"] = None
    except Exception as exception:
        logger.error(exception)

    try:
        if hasattr(data_store.suite, "web3") and data_store.suite["web3"] is not None:
            data_store.suite["web3"].quit()
            data_store.suite["web3"] = None
    except Exception as exception:
        logger.error(exception)
    # Reset Chrome Options
    ChromeOpts()


def clean_up_mobile_driver():
    # ============================== MOBILE ==============================
    try:
        if hasattr(data_store.suite, "mobile") and data_store.suite["mobile"] is not None:
            mobile_driver = data_store.suite["mobile"]
            if mobile_driver.is_app_installed("io.appium.uiautomator2.server") and mobile_driver.is_app_installed("io.appium.uiautomator2.server.test"):
                mobile_driver.remove_app("io.appium.uiautomator2.server")
                mobile_driver.remove_app("io.appium.uiautomator2.server.test")
            mobile_driver.quit()
            data_store.suite["mobile"] = None
    except Exception as exception:
        logger.error(exception)

    try:
        if hasattr(data_store.suite, "appium_service"):
            data_store.suite.appium_service.stop()
    except Exception as exception:
        logger.error(exception)


def config_report_settings():
    try:
        if data_store.suite.license is False:
            data_store.suite.days_to_keep_reports = 7
        else:
            data_store.suite.days_to_keep_reports = 3650
        report_path = os.path.join(PROJECT_PATH, "reports", "html-report")
        list_folder = os.listdir(report_path)
        today = date.today()
        for item in list_folder:
            if len(item.split("-")) == 3 and len(item.split(" ")) == 2:
                rp = item.split(" ")[0].split("-")
                report_date = date(int(rp[0]), int(rp[1]), int(rp[2]))
                delta = today - report_date
                if delta.days >= data_store.suite.days_to_keep_reports:
                    rp_folder = os.path.join(report_path, item)
                    shutil.rmtree(rp_folder)
    except Exception as exception:
        logger.error(exception)


def init_spec_testing_type(context):
    try:
        testing_types = []
        with open(context.specification.file_name, "r", encoding="utf-8") as data:
            for line in data:
                if line.strip().startswith("*"):
                    cswa = convert_step_with_arg(line)
                    file_path, line_number = find_file_related_to_step(cswa)
                    test_type = get_testing_type_in_file(file_path, line_number)
                    if test_type is not None:
                        testing_types.append(test_type)
        return list(dict.fromkeys(testing_types))
    except Exception as exception:
        logger.error(exception)
        return list(dict.fromkeys(testing_types))


def init_step_testing_type(context):
    try:
        cswa = convert_step_with_arg(context.step.text)
        file_path, line_number = find_file_related_to_step(cswa)
        test_type = get_testing_type_in_file(file_path, line_number)
        return test_type if test_type is not None else None
    except Exception as exception:
        logger.error(exception)
        return None


def convert_step_with_arg(step: str):
    try:
        st = step.strip()
        result = re.findall('"(.+?)"', st)
        for item in result:
            st = st.replace(f'"{item}"', "arg")
        result = re.findall("<(.+?)>", st)
        for item in result:
            st = st.replace(f"<{item}>", "arg")
        return st
    except Exception as exception:
        logger.error(exception)


def find_file_related_to_step(step_with_arg: str):
    try:
        file_path = None
        line_number = None
        for path, subdirs, files in os.walk(PROJECT_PATH):
            for name in files:
                if name[-3:] == ".py":
                    file_path = os.path.join(path, name)
                    with open(file_path, "r", encoding="utf-8") as data:
                        line_number = 0
                        for line in data:
                            line_number = line_number + 1
                            sf = line.strip()
                            # if sf.startswith('@step'):
                            result = re.findall("<(.+?)>", sf)
                            if result:
                                for item in result:
                                    sf = sf.replace(f"<{item}>", "arg")
                            if step_with_arg in sf:
                                return file_path, line_number
    except Exception as exception:
        logger.error(exception)


def get_testing_type_in_file(file_path, line_number):
    try:
        count = 0
        test_type = None
        with open(file_path, "r", encoding="utf-8") as data:
            for line in data:
                if count > line_number:
                    break
                result = re.findall(r"class (.+?)\):", line)
                if result:
                    test_type = re.search(r"\((.*)\)", line)
                    test_type = test_type[1]
                count = count + 1
        return test_type
    except Exception as exception:
        logger.error(exception)


def g_c_o_s(screenshot_as_base64):
    try:
        result = []
        img = Image.open(BytesIO(base64.b64decode(screenshot_as_base64)))
        pixel_count = img._size[0] * img._size[1]
        list_color = img.getcolors(256**2 * 256)
        list_color.sort(reverse=True)
        for color in list_color:
            color_red = hex(color[1][0]).replace("0x", "0")[-2:].upper()
            color_green = hex(color[1][1]).replace("0x", "0")[-2:].upper()
            color_blue = hex(color[1][2]).replace("0x", "0")[-2:].upper()
            obj = (
                round(color[0] * 100 / pixel_count, 3),
                f"#{color_red}{color_green}{color_blue}",
                color_names.find(f"#{color_red}{color_green}{color_blue}"),
            )
            result.append(obj)
        img.close()
        return result[:10]
    except Exception as exception:
        logger.error(exception)
        return []


def get_latest_log_file():
    try:
        file_list = []
        for path, subdirs, files in os.walk(PROJECT_PATH):
            for name in files:
                if name[-4:] == ".log" and name[:5] == "gauge":
                    file_path = os.path.join(path, name)
                    fname = pathlib.Path(file_path)
                    file_list.append((fname.stat().st_atime, file_path))
        file_list = sorted(file_list, reverse=True)
        return file_list[0][1]
    except Exception as exception:
        logger.error(exception)


def get_execution_tags():
    try:
        for proc_parent in psutil.Process(os.getpid()).parents():
            if proc_parent.name() in ["gauge", "gauge.exe"]:
                cmd = proc_parent.cmdline()
                for arg in cmd:
                    if arg in ["-t", "--tags"]:
                        return cmd[cmd.index(arg) + 1]
                    elif arg.startswith("-t=") or arg.startswith("--tags="):
                        return arg.split("=")[1]
                    elif arg in ["-f", "--failed"]:
                        for path, subdirs, files in os.walk(PROJECT_PATH):
                            for name in files:
                                if name == "failures.json":
                                    file_path = os.path.join(path, name)
                                    with open(file_path, "r", encoding="utf-8") as data:
                                        args = json.load(data)
                                        args = args["Args"]
                                        for arg in args:
                                            if arg in ["-t", "--tags"]:
                                                return args[args.index(arg) + 1]
                                            elif arg.startswith("-t=") or arg.startswith("--tags="):
                                                return arg.split("=")[1]

    except Exception as exception:
        logger.error(exception)
        return None


def replace_in_file(file_path, old_string, new_string):
    try:
        # Create temp file
        fh, abs_path = mkstemp()
        with fdopen(fh, "w") as new_file:
            with open(file_path) as old_file:
                for line in old_file:
                    new_file.write(line.replace(old_string, new_string))
        # Copy the file permissions from the old file to the new file
        copymode(file_path, abs_path)
        # Remove original file
        remove(file_path)
        # Move new file
        move(abs_path, file_path)
    except Exception as exception:
        logger.error(exception)


def init_mobile_platform():
    try:
        load_config()
        data_store.suite.mobile_udid = None
        data_store.suite.execution_tags = get_execution_tags()
        if data_store.suite.execution_tags is None:
            return None
        udid = re.search(r"udid:(.*)?\|", data_store.suite.execution_tags)
        if udid is not None:
            data_store.suite.mobile_udid = udid[1].strip()
        else:
            udid = re.search("udid:(.*)", data_store.suite.execution_tags)
            if udid:
                data_store.suite.mobile_udid = udid[1].strip()
        if data_store.suite.mobile_udid and "|" in data_store.suite.mobile_udid:
            data_store.suite.mobile_udid = data_store.suite.mobile_udid.split("|")[0]
        if data_store.suite.mobile_udid:
            set_mobile_platform_name(data_store.suite.mobile_udid)
    except Exception as exception:
        logger.error(exception)


def get_current_log_line():
    with contextlib.suppress(Exception):
        for path, subdirs, files in os.walk(PROJECT_PATH):
            for name in files:
                if name == "gauge.log":
                    file_path = os.path.join(path, name)
                    with open(file_path, "r", encoding="utf-8") as data:
                        return len(data.readlines())


def escape_ansi(text):
    try:
        ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
        return ansi_escape.sub("", text)
    except Exception as exception:
        logger.error(exception)


def detect_duplicate_function_step():
    try:
        for s_i_d in os.environ.get("STEP_IMPL_DIR").split(","):
            for path, subdirs, files in os.walk(os.path.join(PROJECT_PATH, s_i_d.strip())):
                for name in files:
                    dup_list = []
                    if name[-3:] == ".py":
                        file_path = os.path.join(path, name)
                        function_list = []
                        if os.path.exists(file_path):
                            with open(file_path, "r", encoding="utf-8") as data:
                                for line in data:
                                    if line.strip().startswith("def ") and "(" in line.strip() and ")" in line.strip() and ":" in line.strip():
                                        item = line.strip().split("(")[0].split("def")[1].strip()
                                        function_list.append(item)

                        dup_list.extend(i for i in function_list if function_list.count(i) > 1)
                        if dup_list:
                            dup_list = list(dict.fromkeys(dup_list))
                            for dup in dup_list:
                                for s_i_d in os.environ.get("STEP_IMPL_DIR").split(","):
                                    for path, subdirs, files in os.walk(os.path.join(PROJECT_PATH, s_i_d.strip())):
                                        for name in files:
                                            if name[-3:] == ".py":
                                                file_path = os.path.join(path, name)
                                                with open(file_path, "r", encoding="utf-8") as data:
                                                    for inline, line in enumerate(data, start=1):
                                                        if line.strip().startswith(f"def {dup}(") and ")" in line.strip() and ":" in line.strip():
                                                            # item = line.strip().split('(')[0].split('def')[1].strip()
                                                            logger.warning(f"- Function: '{dup}' is duplicated name in {file_path}:{inline}")

        return False
    except Exception as exception:
        logger.error(exception)
        return False
