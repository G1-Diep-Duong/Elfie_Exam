import base64
import json
import platform
import time
from io import BytesIO

from appium import webdriver as Appium_WebDriver
from appium.webdriver.webelement import WebElement as MobileWebElement
from getgauge.python import Messages, Screenshots, data_store
from PIL import Image
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .utils import color_names, gauge_wrap, logger
from .utils.adb_util import ADBUtil
from .utils.string_util import StringUtil

# ====================================================================================================
#                         MOBILE BASE SCREEN
# ====================================================================================================


class BaseScreen(object):
    __DEFAULT_TIMEOUT = 10
    _driver: Appium_WebDriver.Remote
    _actions: ActionChains
    _adb: ADBUtil

    @gauge_wrap
    def __detect_locator(self, element_locator):
        try:
            if len(element_locator[0]) > 1:
                if self._driver.caps.get("platformName").lower() == "android":
                    locator_value = element_locator[0]
                else:
                    locator_value = element_locator[1]
            else:
                locator_value = element_locator
            by_type = "xpath" if ("//" in locator_value) else "id"
            return locator_value, by_type
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def format_locator(self, based_element_locator, *sub_string):
        try:
            return StringUtil.format_string(self.__detect_locator(based_element_locator)[0], *sub_string)
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def __type(self, element_locator, text: str, clear_first=True, timeout_in_seconds: int = None):
        """Type element by element_locator
        Args:
            element_locator (_type_): _description_
            text (str): _description_
        """
        start_time = time.time()
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return False
        try:
            if clear_first:
                self.__clear(element_locator)
            element = self.find_element(element_locator, timeout, False)
            if element is not None:
                element.send_keys(text)
                return True
            return False
        except Exception as exception:
            if type(exception).__name__ in ["StaleElementReferenceException"]:
                return self.__type(element_locator=element_locator, text=text, clear_first=clear_first, timeout_in_seconds=timeout - (time.time() - start_time + 1))
            else:
                logger.error(exception)
            return False

    @gauge_wrap
    def __clear(self, element_locator, timeout_in_seconds: int = None):
        """Clear an element's value"""
        start_time = time.time()
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return False
        try:
            element = self.find_element(element_locator, timeout)
            if element is not None:
                element.clear()
                return True
            return False
        except Exception as exception:
            if type(exception).__name__ in ["StaleElementReferenceException"]:
                return self.__clear(element_locator, timeout_in_seconds=timeout - (time.time() - start_time + 1))
            else:
                logger.error(exception)
            return False

    @gauge_wrap
    def __click(self, element_locator, timeout_in_seconds: int = None):
        """Click element by element locator
        Args:
            element_locator (_type_): _description_
            timeout_in_seconds (int, optional): _description_. Defaults to None.
        Returns:
            _type_: _description_
        """
        start_time = time.time()
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return False
        try:
            element = self.find_element(element_locator, timeout)
            return False if element is None else element.click() is None
        except Exception as exception:
            if type(exception).__name__ in ["ElementNotInteractableException"]:
                self.move_to(element_locator)
                return self.__click(element_locator, timeout_in_seconds=timeout - (time.time() - start_time + 1))
            if type(exception).__name__ in ["StaleElementReferenceException"]:
                return self.__click(element_locator, timeout_in_seconds=timeout - (time.time() - start_time + 1))
            if type(exception).__name__ not in ["ElementClickInterceptedException", "ElementNotInteractableException", "StaleElementReferenceException"]:
                logger.error(exception)
                if data_store.suite.license:
                    Messages.write_message(exception)
                return False

    @gauge_wrap
    def __get_colors_of_element(self, element, number_of_colors=20):
        """
        Get a list color of image as each info: (percent of color in image, #code color as HEX)
        e.g. (56.361, '#FFBB00') means color Selective Yellow (#FFBB00) displayed as 56.361% in the image
        Args:
            element_locator (Locator)
            number_of_colors (int, optional): [Number of colors to get]. Defaults to 20.
        Returns:
            list: color list
        """
        try:
            if element is None:
                return None
            result = []
            # img = Image.open(BytesIO(base64.b64decode(element.screenshot_as_base64)))
            with Image.open(BytesIO(base64.b64decode(element.screenshot_as_base64))) as img:
                pixel_count = img._size[0] * img._size[1]
                list_color = img.getcolors(256**2 * 256)
                list_color.sort(reverse=True)
                for color in list_color:
                    color_red = hex(color[1][0]).replace("0x", "0")[-2:].upper()
                    color_green = hex(color[1][1]).replace("0x", "0")[-2:].upper()
                    color_blue = hex(color[1][2]).replace("0x", "0")[-2:].upper()
                    obj = (round(color[0] * 100 / pixel_count, 3), f"#{color_red}{color_green}{color_blue}", color_names.find(f"#{color_red}{color_green}{color_blue}"))
                    result.append(obj)
            # img.close()
            return result[:number_of_colors]
        except Exception as exception:
            logger.error(exception)
            return None

    @gauge_wrap
    def __get_color_names_of_element(self, element, number_of_color_names=10):
        try:
            if element is None:
                return None
            temp = []
            color_list = []
            result = []
            colors = self.__get_colors_of_element(element, 1000)
            for color in colors:
                obj = (color[0], color_names.find(color[1]))
                temp.append(obj)
            for color in temp:
                if color[1] not in color_list:
                    color_list.append(color[1])
            for color in color_list:
                count = sum(obj[0] for obj in temp if color == obj[1])
                count = 0.001 if round(count, 3) == 0.0 else round(count, 3)
                result.append((count, color))
            result.sort(reverse=True)
            return result[:number_of_color_names]
        except Exception as exception:
            logger.error(exception)
            return None

    @gauge_wrap
    def generate_element_xpath(self, element: MobileWebElement):
        """
        - Generate xpath of element at current time.
        """
        try:
            if element is None:
                return None
            if self.is_element_stale(element):
                logger.warning("The element is stale, please check it again !!!")
                return None
            xpath = "//*"
            atts = ["type", "name", "rect"] if data_store.suite.mobile_platform_name.lower() == "ios" else ["package", "class", "resource-id", "bounds"]
            for att in atts:
                value = element.get_attribute(att)
                if value:
                    if att == "rect":
                        rect = json.loads(value)
                        for key in rect:
                            xpath += f'[@{key}="{rect[key]}"]'
                    elif '"' not in value:
                        xpath += f'[@{att}="{value}"]'
            return xpath
        except Exception as exception:
            logger.error(exception)
            return None

    @gauge_wrap
    def swipe_screen(self, direction: str = "up", percentage: int = 50, duration: int = 0):
        """
        Swipe the screen in one direction based on screen percentage.
        Args:
            direction: 'up' | 'down' | 'left' | 'right'
            percentage: Percent of Screen to swipe: int, default is 50 means a half of screen to be scrolled
            duration: defines the swipe speed as time taken to swipe in ms, default is 0 means the speed is set automatically
        Usage:
            - Swipe up 69% of screen in 5,874 seconds:
            driver.swipe(direction = 'up', percentage = 69, duration = 5874)
        """
        try:
            if percentage <= 0:
                percentage = 1
            percent = percentage / 100
            window_size = self._driver.get_window_size()
            start_x = int(window_size["width"] / 2)
            start_y = int(window_size["height"] / 2)
            if direction.lower() == "up":
                end_x = start_x
                end_y = int(start_y - (window_size["height"] * percent))
                if duration < 1:
                    duration = int(pow(pow(end_y - start_y, 2), 1 / 2) * 2)
            if direction.lower() == "down":
                end_x = start_x
                end_y = int(start_y + (window_size["height"] * percent))
                if duration < 1:
                    duration = int(pow(pow(end_y - start_y, 2), 1 / 2) * 2)
            if direction.lower() == "left":
                end_x = int(start_x - (window_size["width"] * percent))
                end_y = start_y
                if duration < 1:
                    duration = int(pow(pow(end_x - start_x, 2), 1 / 2) * 2)
            if direction.lower() == "right":
                end_x = int(start_x + (window_size["width"] * percent))
                end_y = start_y
                if duration < 1:
                    duration = int(pow(pow(end_x - start_x, 2), 1 / 2) * 2)
            self._driver.swipe(start_x, start_y, end_x, end_y, duration)
            return True
        except Exception as exception:
            logger.error(exception)
            return False

    # ====================================================================================================
    #                         CONTROL METHODS
    # ====================================================================================================

    @gauge_wrap
    def find_element(self, element_locator, timeout_in_seconds: int = None, show_log=True) -> MobileWebElement:
        """
        [Find an element within a timeout in seconds.]
        Raises:
            NoSuchElementException: [if Element not found]
        Returns:
            [WebElement]: [WebElement if found]
        """
        start_time = time.time()
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return None
        locator_value, by_type = self.__detect_locator(element_locator)
        try:
            return WebDriverWait(self._driver, timeout).until(EC.presence_of_element_located((by_type, locator_value)))
        except Exception as exception:
            if type(exception).__name__ in ["StaleElementReferenceException"]:
                return self.find_element(element_locator, timeout_in_seconds=timeout - (time.time() - start_time + 1))
            if type(exception).__name__ == "TimeoutException":
                message = f"Element NOT found with locator {by_type}: '{locator_value}' after {(time.time() - start_time):.3f} seconds"
                if show_log:
                    logger.error(message)
                    if data_store.suite.license:
                        Messages.write_message(message)
            else:
                message = str(exception)
                if show_log:
                    logger.error(message)
            return None

    @gauge_wrap
    def find_elements(self, element_locator, timeout_in_seconds: int = None, show_log=True):
        """
        [Find elements within a timeout in seconds.]
        Raises:
            NoSuchElementException: [if Elements not found]
        Returns:
            List[WebElement]: [WebElements if found]
        """
        start_time = time.time()
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return []
        locator_value, by_type = self.__detect_locator(element_locator)
        try:
            return WebDriverWait(self._driver, timeout).until(EC.presence_of_all_elements_located((by_type, locator_value)))
        except Exception as exception:
            if type(exception).__name__ in ["StaleElementReferenceException"]:
                return self.find_elements(element_locator, timeout_in_seconds=timeout - (time.time() - start_time + 1))
            if show_log:
                if type(exception).__name__ == "TimeoutException":
                    message = f"Elements not found with locator {by_type}: '{locator_value}' after {time.time() - start_time:.3f} seconds !!!"
                    logger.error(message)
                    if data_store.suite.license:
                        Messages.write_message(message)
                else:
                    logger.error(exception)
            return []

    @gauge_wrap
    def clear_element_by_action_chains(self, element_locator):
        try:
            element = self.find_element(element_locator)
            element.clear()
            element.click()
            for _ in range(len(element.text)):
                self._driver.press_keycode(67)
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def move_to(self, element_locator):
        """
        Moving the mouse to the middle of an element.
        :Args:
            element_locator
        """
        try:
            self.move_to_element(self.find_element(element_locator))
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def move_to_element(self, element: MobileWebElement):
        """
        Moving the mouse to the middle of an element.
        :Args:
            element (MobileWebElement)
        """
        try:
            if element is None:
                return False
            if self.is_element_stale(element):
                logger.warning("The element is stale, please check it again !!!")
                return False
            action_chains = ActionChains(self._driver)
            action_chains.move_to_element(element).perform()
            return True
        except Exception as exception:
            logger.error(exception)
            return False

    @gauge_wrap
    def tap_enter_by_action_chains(self):
        try:
            action_chains = ActionChains(self._driver)
            action_chains.send_keys(Keys.ENTER)
            action_chains.perform()
            action_chains.release()
            return True
        except Exception as exception:
            logger.error(exception)
            return False

    @gauge_wrap
    def type_by_action_chains(self, element_locator=None, text="", clear_element=True):
        try:
            if element_locator is not None and clear_element:
                self.clear_element_by_action_chains(element_locator)
            if element_locator is not None:
                self.click(element_locator)
            action_chains = ActionChains(self._driver)
            action_chains.send_keys(text).perform()
            return True
        except Exception as exception:
            logger.error(exception)
            return False

    @gauge_wrap
    def click_element(self, element: MobileWebElement):
        try:
            if self.is_element_stale(element):
                logger.warning("The element is stale, please check it again !!!")
            if element is not None:
                xpath = self.generate_element_xpath(element)
            return element.click() is None if element is not None else False
        except Exception as exception:
            if type(exception).__name__ in ["ElementNotInteractableException"]:
                self.move_to_element(element)
                return element.click() is None
            if type(exception).__name__ in ["StaleElementReferenceException"]:
                if xpath is None:
                    return False
                self.find_element(xpath).click()
            if type(exception).__name__ not in ["ElementClickInterceptedException", "ElementNotInteractableException", "StaleElementReferenceException"]:
                logger.error(exception)
                return False

    @gauge_wrap
    def double_click(self, element_locator, timeout_in_seconds: int = None):
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return False
        try:
            element = self.find_element(element_locator, timeout)
            if element is not None:
                action_chains = ActionChains(self._driver)
                action_chains.double_click(element).perform()
            else:
                message = "Element NOT found for double clicking !!!"
                logger.warning(message)
                if data_store.suite.license:
                    Messages.write_message(message)
            return True
        except Exception as exception:
            logger.error(exception)
            return False

    # ====================================================================================================
    #                         ELEMENT PROPERTY METHODS
    # ====================================================================================================

    @gauge_wrap
    def is_element_displayed(self, element_locator, timeout_in_seconds=None, show_log=True):
        """Determine if an element is currently displayed.
        Args:
            element_locator (_type_)
            timeout_in_seconds (_type_, optional)
            show_log (bool, optional)
        Returns:
            Return true if the selected DOM-element is displayed.
        """
        try:
            result = self.wait_for_element_displayed(element_locator, timeout_in_seconds, False)
            if show_log:
                if result:
                    logger.debug(f"Element «{element_locator}» is displayed.")
                else:
                    logger.debug(f"Element «{element_locator}» is NOT displayed.")
            return result
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def is_element_stale(self, element: MobileWebElement):
        """
        Returns true if element is stale in the DOM else false.
        """
        try:
            element.location
            return False
        except Exception as exception:
            if type(exception).__name__ in ["StaleElementReferenceException"]:
                return True

    @gauge_wrap
    def wait_for_element_displayed(self, element_locator, timeout_in_seconds=None, show_log=True):
        """Wait for an element for the provided amount of seconds to be displayed or not displayed.
        Args:
            element_locator (_type_)
            timeout_in_seconds (_type_, optional)
            show_log (bool, optional)

        Returns:
            True if element is displayed else False
        """
        try:
            start_time = time.time()
            timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
            if timeout <= 0:
                return False
            while time.time() - start_time - 1 <= timeout and not (self.find_element(element_locator, 1, False) is not None and self.find_element(element_locator, 1, False).is_displayed()):
                pass
            if self.find_element(element_locator, 1, False) is None:
                message = f"Element «{element_locator}» is NOT found after {time.time() - start_time:.3f} seconds !!!"
                result = False
            elif not self.find_element(element_locator, 1, False).is_displayed():
                message = f"Element «{element_locator}» is still NOT displayed after waiting {time.time() - start_time:.3f} seconds !!!"
                result = False
            else:
                message = f"Element «{element_locator}» is displayed after waiting {time.time() - start_time:.3f} seconds !!!"
                result = True
            if show_log:
                logger.debug(message)
            return result
        except Exception as exception:
            logger.error(exception)
            return False

    @gauge_wrap
    def wait_for_element_disappeared(self, element_locator, timeout_in_seconds=None, show_log=True):
        """Wait for an element for the provided amount of seconds to be disappeared or not disappeared.
        Args:
            element_locator (_type_)
            timeout_in_seconds (_type_, optional)
            show_log (bool, optional)
        Returns:
            True if element is disappeared else False
        """
        try:
            start_time = time.time()
            timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
            self.wait_for_element_displayed(element_locator, timeout, False)
            if self.find_element(element_locator, 1, False) is None:
                message = f"Element «{element_locator}» is NOT existed after waiting {time.time() - start_time:.3f} seconds!!!"
                result = False
            while time.time() - start_time - 1 <= timeout and self.wait_for_element_displayed(element_locator, 1, show_log=False):
                pass
            if self.find_element(element_locator, 1, False) is None:
                message = f"Element «{element_locator}» is disappeared after waiting {time.time() - start_time:.3f} seconds !!!"
                result = True
            elif self.find_element(element_locator, 1, False).is_displayed():
                message = f"Element «{element_locator}» is still displayed after waiting {time.time() - start_time:.3f} seconds!!!"
                result = False
            else:
                message = f"Element «{element_locator}» is disappeared after {time.time() - start_time:.3f} seconds!!!"
                result = True
            if show_log:
                logger.debug(message)
            return result
        except Exception as exception:
            if type(exception).__name__ in ["StaleElementReferenceException"]:
                return self.wait_for_element_disappeared(element_locator, timeout_in_seconds=timeout - (time.time() - start_time + 1))
            logger.error(exception)
            return False

    @gauge_wrap
    def wait_for_element_to_change_attribute(self, element_locator, attribute, timeout_in_seconds=None, show_log=True):
        """Wait for element to change attribute
        Args:
            element_locator (_type_)
            attribute
            timeout_in_seconds (_type_, optional)
            show_log (bool, optional)
        Returns:
            True if element's attribute is changed else False
        """
        try:
            start_time = time.time()
            timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
            if timeout <= 0:
                return False
            beginning_attribute_value = self.get_attribute(element_locator, attribute, timeout - (time.time() - start_time + 1))
            if beginning_attribute_value is not None:
                while time.time() - start_time - 1 <= timeout and self.get_attribute(element_locator, attribute, 1) == beginning_attribute_value:
                    pass
                if self.get_attribute(element_locator, attribute, 1) != beginning_attribute_value:
                    message = f'Attribute "{attribute}" of Element «{element_locator}» has been changed after waiting {time.time() - start_time:.3f} seconds!!!'
                    result = True
                else:
                    message = f'Attribute "{attribute}" of Element «{element_locator}» has NOT been changed after waiting {time.time() - start_time:.3f} seconds!!!'
                    result = False
            else:
                message = f'Attribute "{attribute}" of Element «{element_locator}» is NOT existed !!!'
                result = False
            if show_log:
                logger.debug(message)
            return result
        except Exception as exception:
            logger.error(exception)
            return False

    @gauge_wrap
    def is_element_existing(self, element_locator, timeout_in_seconds=None):
        """Returns true if element exists in the DOM.
        Args:
            element_locator (_type_):
            timeout_in_seconds (_type_, optional): timeout in seconds.
        Returns:
            Returns true if element exists in the DOM.
        """
        try:
            return self.find_element(element_locator, timeout_in_seconds) is not None
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def get_text(self, element_locator, timeout_in_seconds=None) -> str:
        """Get the text content from a DOM-element. Make sure the element you want to request the text from is interactable otherwise you will get an empty string as return value.
        Args:
            element_locator (_type_):
            timeout_in_seconds (_type_, optional): Defaults to None.
        Returns:
            str: text of element
        """
        start_time = time.time()
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return None
        try:
            element = self.find_element(element_locator, timeout)
            return element.text
        except Exception as exception:
            if type(exception).__name__ == "StaleElementReferenceException":
                self.get_text(element_locator, timeout - (time.time() - start_time + 1))
            else:
                logger.error(exception)
                return None

    @gauge_wrap
    def get_attribute(self, element_locator, attribute, timeout_in_seconds=None):
        start_time = time.time()
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return None
        try:
            element = self.find_element(element_locator, timeout_in_seconds)
            if element is not None:
                attribute_value = element.get_attribute(attribute)
                if attribute_value is None:
                    message = f"Element «{element_locator}» does NOT have attribute «{attribute}» !!!"
                    logger.warning(message)
                    if data_store.suite.license:
                        Messages.write_message(message)
                return attribute_value
        except Exception as exception:
            if type(exception).__name__ == "StaleElementReferenceException":
                self.get_attribute(element_locator, attribute, timeout - (time.time() - start_time + 1))
            else:
                logger.error(exception)
                return None

    @gauge_wrap
    def get_colors(self, element_locator, number_of_colors=20):
        """
        Get a list color of image as each info: (percent of color in image, #code color as HEX)
        e.g. (56.361, '#FFBB00') means color Selective Yellow (#FFBB00) displayed as 56.361% in the image
        Args:
            element_locator (Locator)
            number_of_colors (int, optional): [Number of colors to get]. Defaults to 20.
        Returns:
            list: color list
        """
        try:
            element = self.find_element(element_locator)
            return self.__get_colors_of_element(element, number_of_colors)
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def get_color_names(self, element_locator, number_of_color_names=10):
        element = self.find_element(element_locator)
        return self.__get_color_names_of_element(element, number_of_color_names)

    @gauge_wrap
    def get_element_all_attributes(self, element):
        try:
            return self._driver.execute_script("var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;", element)
        except Exception as exception:
            logger.error(exception)
            return None

    # ==================================================
    # ALIAS ACTION METHODS
    # ==================================================

    @gauge_wrap
    def click(self, element_locator, timeout_in_seconds: int = None):
        return self.__click(element_locator, timeout_in_seconds)

    @gauge_wrap
    def tap(self, element_locator, timeout_in_seconds: int = None):
        return self.__click(element_locator, timeout_in_seconds)

    @gauge_wrap
    def type(self, element_locator, text: str, clear_first=True, timeout_in_seconds: int = None):
        return self.__type(element_locator, text, clear_first, timeout_in_seconds)

    @gauge_wrap
    def clear(self, element_locator, timeout_in_seconds: int = None):
        return self.__clear(element_locator, timeout_in_seconds)

    @gauge_wrap
    def dynamic_locator(self, based_element_locator, *sub_string):
        return self.format_locator(based_element_locator, *sub_string)

    @gauge_wrap
    def swipe_up(self, percentage: int = 50, duration: int = 0):
        """
        Swipe up the screen based on screen percentage.
        Args:
            percentage: Percent of Screen to swipe: int, default is 50 means a half of screen to be scrolled
            duration: defines the swipe speed as time taken to swipe in miliseconds, default is 0 means the speed is set automatically
        """
        self.swipe_screen(direction="up", percentage=percentage, duration=duration)

    @gauge_wrap
    def swipe_down(self, percentage: int = 50, duration: int = 0):
        """
        Swipe down the screen based on screen percentage.
        Args:
            percentage: Percent of Screen to swipe: int, default is 50 means a half of screen to be scrolled
            duration: defines the swipe speed as time taken to swipe in miliseconds, default is 0 means the speed is set automatically
        """
        self.swipe_screen(direction="down", percentage=percentage, duration=duration)

    @gauge_wrap
    def swipe_left(self, percentage: int = 50, duration: int = 0):
        """
        Swipe left the screen based on screen percentage.
        Args:
            percentage: Percent of Screen to swipe: int, default is 50 means a half of screen to be scrolled
            duration: defines the swipe speed as time taken to swipe in miliseconds, default is 0 means the speed is set automatically
        """
        self.swipe_screen(direction="left", percentage=percentage, duration=duration)

    @gauge_wrap
    def swipe_right(self, percentage: int = 50, duration: int = 0):
        """
        Swipe right the screen based on screen percentage.
        Args:
            percentage: Percent of Screen to swipe: int, default is 50 means a half of screen to be scrolled
            duration: defines the swipe speed as time taken to swipe in miliseconds, default is 0 means the speed is set automatically
        """
        self.swipe_screen(direction="right", percentage=percentage, duration=duration)

    # ====================================================================================================
    # PAGE METHODS
    # ====================================================================================================

    @gauge_wrap
    def capture_element_screenshot(self, element: MobileWebElement):
        """
        Capture a screenshot of the element to a PNG file on your report folder.
        """
        try:
            if self.is_element_stale(element):
                logger.warning("The element is stale, please check it again !!!")
            if element is None:
                logger.warning("Cannot capture element which is not existed !!!")
            elif element.size["height"] > 0 and element.size["width"] > 0:
                data_store.suite.capture_element_screenshot = element
                data_store.suite.capture_element_screenshot_time = time.time()
                Screenshots.capture_screenshot()
            else:
                logger.warning(f"Cannot capture element which has size {element.size} !!!")
        except Exception as exception:
            logger.error(exception)
        finally:
            data_store.suite.capture_element_screenshot = None

    @gauge_wrap
    def capture_element_screenshot_by_locator(self, element_locator):
        """
        Capture a screenshot of the element by element's locator to a PNG file on your report folder.
        """
        try:
            self.capture_element_screenshot(self.find_element(element_locator))
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def capture_screen_screenshot(self):
        """
        Capture a screenshot of the current browsing context to a PNG file on your report folder.
        """
        try:
            data_store.suite.capture_element_screenshot = None
            Screenshots.capture_screenshot()
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def back(self):
        """Goes one step backward in the browser history."""
        try:
            self._driver.back()
        except Exception as exception:
            logger.error(exception)
            if data_store.suite.license:
                Messages.write_message(exception)

    @gauge_wrap
    def forward(self):
        try:
            self._driver.forward()
        except Exception as exception:
            logger.error(exception)
            if data_store.suite.license:
                Messages.write_message(exception)


# ====================================================================================================
#                         ENTITY
# ====================================================================================================


class MobileScreen(BaseScreen):
    _driver: Appium_WebDriver.Remote
    _actions: ActionChains
    _adb: ADBUtil

    def init(driver):  # sourcery skip: instance-method-first-arg-name
        try:
            if driver is not None:
                MobileScreen._KEY_CONTROL = Keys.COMMAND if platform.system() != "Windows" else Keys.CONTROL
                MobileScreen._driver: Appium_WebDriver.Remote = driver
                MobileScreen._actions = ActionChains(driver)
                MobileScreen._platform = str(driver.capabilities["platformName"]).lower()
                if str(driver.capabilities["platformName"]).lower() != "ios":
                    MobileScreen._adb = ADBUtil(driver.caps.get("udid"))
                else:
                    MobileScreen._adb = None
        except Exception as exception:
            logger.error(exception)

    def clear_data(self, package):
        """
        Deletes all data associated with a package.
        """
        try:
            return self._adb.clear_data(package).strip()
        except Exception as exception:
            logger.error(exception)
