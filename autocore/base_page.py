import base64
import json
import os
import platform
import time
from io import BytesIO
from multiprocessing import Pool

import cv2

# import Image
import numpy as np
import pkg_resources
import pyautogui
from appium import webdriver as Appium_WebDriver

from getgauge.python import Messages, Screenshots, data_store
from PIL import Image
from screeninfo import get_monitors
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from .utils import color_names, gauge_wrap, logger, timing
from .utils.API_request import APIRequest
from .utils.image_util import get_box
from .utils.string_util import StringUtil


class BasePage(object):
    __DEFAULT_TIMEOUT = 20
    _driver: WebDriver
    _actions: ActionChains
    __KEY_CONTROL = Keys.CONTROL if platform.system() == "Windows" else Keys.COMMAND
    _loc: str

    # ====================================================================================================
    #                         CONTROL METHODS
    # ====================================================================================================

    @gauge_wrap
    def __detect_locator(self, element_locator):
        try:
            if element_locator is None:
                logger.warning(f"The locator is {element_locator}, please check again !!!")
                return None, None
            locator_value = element_locator
            by_type = "xpath" if ("//" in locator_value) else "id"
            return locator_value, by_type
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def format_locator(self, based_element_locator, *sub_string):
        """Use to generate dynamic locator
        Args:
            based_element_locator: based locator
            *sub_string: strings to replace into based locator
        Returns:
            dynamic locator
        e.g:\n
        self.format_locator('//*[text()="%s"]', 'selenium') -> //*[text()="selenium"]\n
        self.format_locator('//*[text()="%s - %s"]', "Selenium", "Appium") -> //*[text()="Selenium - Appium"]
        """
        try:
            return StringUtil.format_string(self.__detect_locator(based_element_locator)[0], *sub_string)
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def find_element(self, element_locator, timeout_in_seconds: int = None, show_log=True) -> WebElement:
        """
        [Find an element within a timeout in seconds.]
        Raises:
            NoSuchElementException: [if Element not found]
        Returns:
            [WebElement]: [WebElement if found]
        """
        start_time = time.time()
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        locator_value, by_type = self.__detect_locator(element_locator)
        if locator_value is None:
            return None
        try:
            return None if timeout <= 0 else WebDriverWait(self._driver, timeout).until(EC.presence_of_element_located((by_type, locator_value)))
        except Exception as exception:
            if type(exception).__name__ in ["StaleElementReferenceException"]:
                return self.find_element(element_locator, timeout_in_seconds=timeout - (time.time() - start_time + 1))
            if type(exception).__name__ == "TimeoutException":
                message = f"Element NOT found with locator {by_type}: '{locator_value}' after {(time.time() - start_time):.3f} seconds"
                if show_log:
                    logger.debug(message)
                    if data_store.suite.license:
                        Messages.write_message(message)
            else:
                message = str(exception)
                if show_log:
                    logger.error(message)
                    if data_store.suite.license:
                        Messages.write_message(message)
            return None

    @gauge_wrap
    def find_elements(self, element_locator, timeout_in_seconds: int = None, show_log=True) -> list[WebElement]:
        """
        [Find elements within a timeout in seconds.]
        Raises:
            NoSuchElementException: [if Elements not found]
        Returns:
            List[WebElement]: [WebElements if found]
        """
        start_time = time.time()
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        locator_value, by_type = self.__detect_locator(element_locator)
        if locator_value is None:
            return None
        try:
            return [] if timeout <= 0 else WebDriverWait(self._driver, timeout).until(EC.presence_of_all_elements_located((by_type, locator_value)))
        except Exception as exception:
            if type(exception).__name__ in ["StaleElementReferenceException"]:
                return self.find_elements(element_locator, timeout_in_seconds=timeout - (time.time() - start_time + 1))
            if type(exception).__name__ == "TimeoutException":
                message = f"Elements not found with locator {by_type}: '{locator_value}' after {time.time() - start_time:.3f} seconds"
                if show_log:
                    logger.debug(message)
                    if data_store.suite.license:
                        Messages.write_message(message)
            else:
                message = str(exception)
                if show_log:
                    logger.error(message)
                    if data_store.suite.license:
                        Messages.write_message(message)
            return []

    @gauge_wrap
    def __type(self, element_locator, text: str, clear_first: bool = True, timeout_in_seconds: int = None):
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
                self.__clear(element_locator, timeout)
            element = self.find_element(element_locator, timeout - (time.time() - start_time + 1))
            return False if element is None else element.send_keys(text) is None
        except Exception as exception:
            if type(exception).__name__ in ["ElementNotInteractableException"]:
                self.move_to(element_locator, timeout_in_seconds=timeout - (time.time() - start_time + 1))
                return self.__type(element_locator=element_locator, text=text, clear_first=clear_first, timeout_in_seconds=timeout - (time.time() - start_time + 1))
            logger.error(exception)
            return False

    @gauge_wrap
    def __clear(self, element_locator, timeout_in_seconds: int = None):
        """Clears the text if it's a text entry element."""
        start_time = time.time()
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return False
        try:
            element = self.find_element(element_locator, timeout)
            if element is None:
                return False

            parent = element._parent
            if "selenium.webdriver.chrome" in str(type(parent)):
                element_value = element.get_attribute("value")
                if len(element_value) > 0:
                    for _ in element_value:
                        element.send_keys(Keys.BACK_SPACE)
            return element.clear() is None
        except Exception as exception:
            if type(exception).__name__ in ["ElementNotInteractableException"]:
                self.move_to(element_locator, timeout - (time.time() - start_time + 1))
                return self.__clear(element_locator, timeout - (time.time() - start_time + 1))
            if type(exception).__name__ in ["StaleElementReferenceException", "WebDriverException", "NoSuchWindowException"]:
                return self.__clear(element_locator, timeout - (time.time() - start_time + 1))
            logger.error(exception)
            return False

    @gauge_wrap
    def clear_element_by_action_chains(self, element_locator):
        try:
            self.click(element_locator)
            action_chains = ActionChains(self._driver)
            action_chains.key_down(self.__KEY_CONTROL).send_keys("a").key_up(self.__KEY_CONTROL).perform()
            action_chains.send_keys(Keys.DELETE).perform()
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def move_to(self, element_locator, timeout_in_seconds: int = None):
        start_time = time.time()
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return False
        try:
            element = self.find_element(element_locator, timeout)
            return False if element is None else self.move_to_element(element, timeout - (time.time() - start_time + 1))
        except Exception as exception:
            logger.error(exception)
            return False

    @gauge_wrap
    def move_to_element(self, element: WebElement, timeout_in_seconds: int = None):
        """move_to_element
        Args:
            element (WebElement): [description]
        """
        if self.is_element_stale(element):
            logger.warning("The element is stale, please check it again !!!")
            return False
        start_time = time.time()
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return False
        try:
            action_chains = ActionChains(self._driver)
            action_chains.move_to_element(element).perform()
            return True
        except Exception as exception:
            if type(exception).__name__ in ["ElementNotInteractableException"]:
                self._driver.execute_script("arguments[0].scrollIntoView(false);", element)
                return True
            else:
                logger.error(exception)
            return False

    @gauge_wrap
    def tap_enter_by_action_chains(self):
        try:
            action_chains = ActionChains(self._driver)
            action_chains.send_keys(Keys.ENTER)
            action_chains.perform()
            action_chains.release()
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def type_by_action_chains(self, element_locator=None, text="", clear_element=False):
        try:
            if element_locator is not None and clear_element:
                self.clear_element_by_action_chains(element_locator)
            if element_locator is not None:
                self.click(element_locator)
            action_chains = ActionChains(self._driver)
            action_chains.send_keys(text)
            action_chains.perform()
            action_chains.release()
            return True
        except Exception as exception:
            logger.error(exception)
            return False

    @gauge_wrap
    def paste_text_to_element(self, element_locator=None, text=""):
        # user for copy paste incase can NOT type with non-english character
        try:
            if element_locator is not None:
                self.click(element_locator)
            self._driver.set_clipboard_text(text)
            action_chains = ActionChains(self._driver)
            action_chains.key_down(self.__KEY_CONTROL).send_keys("v").key_up(self.__KEY_CONTROL).perform()
            action_chains.release()
        except Exception as exception:
            logger.error(exception)

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
            return element.click() is None if element is not None else False

        except Exception as exception:
            if type(exception).__name__ in ["ElementClickInterceptedException"]:
                return self.click_element_by_javascript(self.find_element(element_locator, timeout - (time.time() - start_time + 1)))
            if type(exception).__name__ in ["ElementNotInteractableException"]:
                self.move_to(element_locator, timeout - (time.time() - start_time + 1))
                return self.click_element_by_javascript(self.find_element(element_locator, timeout - (time.time() - start_time + 1)))
            if type(exception).__name__ in ["StaleElementReferenceException"]:
                return self.click_element_by_javascript(self.find_element(element_locator, timeout - (time.time() - start_time + 1)))
            if type(exception).__name__ not in ["ElementClickInterceptedException", "ElementNotInteractableException", "StaleElementReferenceException"]:
                logger.warning(exception)
                if data_store.suite.license:
                    Messages.write_message(exception)
                return False

    @gauge_wrap
    def click_element(self, element: WebElement):
        try:
            if self.is_element_stale(element):
                logger.warning("The element is stale, please check it again !!!")
                return False
            if element is not None:
                xpath = self.generate_element_xpath(element)
            return element.click() is None if element is not None else False
        except Exception as exception:
            if type(exception).__name__ in ["ElementClickInterceptedException"]:
                return self.click_element_by_javascript(element)
            if type(exception).__name__ in ["ElementNotInteractableException"]:
                self._driver.execute_script("arguments[0].scrollIntoView(false);", element)
                return self.click_element_by_javascript(element)
            if type(exception).__name__ in ["StaleElementReferenceException"]:
                if xpath is None:
                    return False
                self.find_element(xpath).click()
            if type(exception).__name__ not in ["ElementClickInterceptedException", "ElementNotInteractableException", "StaleElementReferenceException"]:
                logger.error(exception)
                if data_store.suite.license:
                    Messages.write_message(exception)
                return False

    @gauge_wrap
    def click_text(self, sub_text: str, timeout_in_seconds: int = None):
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return False
        try:
            elements = self.find_elements(f'//*[contains(text(),"{sub_text}")]|//*[contains(@placeholder,"{sub_text}")]', timeout, False)
            if not elements:
                logger.warning(f"{sub_text} not found for clicking !!!")
                return False
            for element in elements:
                if element.is_displayed():
                    message = element.text.strip() or element.get_attribute("placeholder")
                    logger.debug(f"Clicking text «{message}» !!!")
                    return self.click_element(element)
            logger.warning(f"«{sub_text}» is not displayed for clicking !!!")
        except Exception as exception:
            logger.error(exception)
            return False

    @gauge_wrap
    def click_image(self, baseline_image=None, button="left", show_log=True):
        try:
            if not os.path.exists(baseline_image):
                logger.warning(f"«{baseline_image}» is not existed !!!")
                return False
            # img = Image.open(image_file_path)
            # list_scale = [*sum(zip(range(100, 102), reversed(range(99, 100))), ())]
            start = time.time()
            box = None
            list_scale = [100, 50, 200]
            confidence = 100
            with Image.open(baseline_image) as img:
                with Image.open(BytesIO(base64.b64decode(self._driver.get_screenshot_as_base64()))) as full_img:
                    min_confidence = 85
                    while box is None and confidence != min_confidence and (time.time() - start) < self.__DEFAULT_TIMEOUT:
                        for confidence in reversed(range(min_confidence, 100)):
                            for scale in list_scale:
                                box = get_box(img, full_img, scale, confidence)
                                if box is not None:
                                    win_rect = self._driver.get_window_rect()
                                    x_image = ((box.left + box.width / 2) / full_img.size[0]) * win_rect["width"]
                                    y_image = ((box.top + box.height / 2) / (win_rect["height"] * full_img.size[0] / win_rect["width"])) * win_rect["height"]
                                    self._actions.w3c_actions.pointer_action.move_to_location(x_image, y_image)
                                    if button.lower() == "left":
                                        self._actions.click().perform()
                                    else:
                                        self._actions.context_click().perform()
                                    if show_log:
                                        message = f"«{baseline_image}» is found in {time.time()-start:.3f} seconds !!!"
                                        logger.debug(message)
                                        if data_store.suite.license:
                                            Messages.write_message(message)
                                    return True
            if show_log:
                message = f"«{baseline_image}» is not detected in {time.time()-start:.3f} seconds !!!"
                logger.warning(message)
                if data_store.suite.license:
                    Messages.write_message(message)
            return False
        except Exception as exception:
            logger.error(exception)
            return False

    @gauge_wrap
    def click_by_action_chains(self, element_locator, timeout_in_seconds: int = None):
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return False
        try:
            element = self.find_element(element_locator, timeout)
            return self.click_element_by_action_chains(element)
        except Exception as exception:
            logger.error(exception)
            return False

    @gauge_wrap
    def click_element_by_action_chains(self, element):
        try:
            if element is not None:
                action_chains = ActionChains(self._driver)
                action_chains.click(element).perform()
                return True
            else:
                message = "Element NOT found for clicking... !!!"
                logger.warning(message)
                if data_store.suite.license:
                    Messages.write_message(message)
                return False
        except Exception as exception:
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
                message = "Element NOT found for double clicking... !!!"
                logger.warning(message)
                if data_store.suite.license:
                    Messages.write_message(message)
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def select_drop_down(self, drop_down_locator, text: str):
        try:
            drop_down_list = Select(self.find_element(drop_down_locator))
            options = drop_down_list.options
            for opt in options:
                if opt.text == text:
                    drop_down_list.select_by_value(opt.get_attribute("value"))
                    return True
            return False
        except Exception as exception:
            logger.error(exception)
            return False

    # =================================================
    # ELEMENT PROPERTY METHODS
    # =================================================
    @gauge_wrap
    def is_element_displayed(self, element_locator, timeout_in_seconds=None, show_log=True):
        """Check element is displayed
        Args:
            element_locator (_type_)
            timeout_in_seconds (_type_, optional)
            show_log (bool, optional)
        Returns:
            True if element is displayed else False
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
    def wait_for_element_displayed(self, element_locator, timeout_in_seconds=None, show_log=True):
        """Wait for element to display
        Args:
            element_locator (_type_)
            timeout_in_seconds (_type_, optional)
            show_log (bool, optional)
        Returns:
            True if element is displayed else False
        """
        start_time = time.time()
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        try:
            while time.time() - start_time - 1 <= timeout and (self.find_element(element_locator, 1, False) is None or not self.find_element(element_locator, 1, False).is_displayed()):
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
                if data_store.suite.license:
                    Messages.write_message(message)
            return result
        except Exception as exception:
            if type(exception).__name__ in ["StaleElementReferenceException"]:
                return self.wait_for_element_displayed(element_locator, timeout_in_seconds=timeout - (time.time() - start_time + 1))
            logger.error(exception)
            return False

    @gauge_wrap
    def wait_for_element_disappeared(self, element_locator, timeout_in_seconds=None, show_log=True):
        """Wait for element to disappear
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
                if data_store.suite.license:
                    Messages.write_message(message)
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
                if data_store.suite.license:
                    Messages.write_message(message)
            return result
        except Exception as exception:
            logger.error(exception)

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
    def is_element_stale(self, element: WebElement):
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
            if element is not None:
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
            element = self.find_element(element_locator, timeout)
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
    def get_element_all_attributes(self, element):
        try:
            return self._driver.execute_script("var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;", element)
        except Exception as exception:
            logger.error(exception)
            return None

    @gauge_wrap
    def get_all_attributes(self, element_locator, timeout_in_seconds=None):
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return None
        try:
            element = self.find_element(element_locator, timeout)
            return None if element is None else self.get_element_all_attributes(element)
        except Exception as exception:
            logger.error(exception)
            return None

    @gauge_wrap
    def generate_element_xpath(self, element: WebElement):
        """
        - Generate xpath of element at current time.
        """
        try:
            if element is None:
                return None
            if self.is_element_stale(element):
                logger.warning("The element is stale, please check it again !!!")
                return None
            xpath = f"//{element.tag_name}"
            element_all_attributes = self.get_element_all_attributes(element)
            if element_all_attributes:
                for att in element_all_attributes:
                    value = element_all_attributes[att]
                    if value and '"' not in value:
                        xpath += f'[@{att}="{value}"]'
            return xpath
        except Exception as exception:
            logger.error(exception)
            return None

    @gauge_wrap
    def get_content_description(self, element_locator):
        return self.get_attribute(element_locator, "content-desc")

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
            result = []
            img = Image.open(BytesIO(base64.b64decode(element.screenshot_as_base64)))
            pixel_count = img._size[0] * img._size[1]
            list_color = img.getcolors(256**2 * 256)
            list_color.sort(reverse=True)
            for color in list_color:
                color_red = hex(color[1][0]).replace("0x", "0")[-2:].upper()
                color_green = hex(color[1][1]).replace("0x", "0")[-2:].upper()
                color_blue = hex(color[1][2]).replace("0x", "0")[-2:].upper()
                obj = (round(color[0] * 100 / pixel_count, 3), f"#{color_red}{color_green}{color_blue}", color_names.find(f"#{color_red}{color_green}{color_blue}"))
                result.append(obj)
            img.close()
            return result[:number_of_colors]
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def get_color_names(self, element_locator, number_of_color_names=10):
        element = self.find_element(element_locator)
        return self.__get_color_names_of_element(element, number_of_color_names)

    @gauge_wrap
    def __get_color_names_of_element(self, element, number_of_color_names=10):
        try:
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

    @gauge_wrap
    def swipe_page(self, direction: str = "up", percentage: int = 50):
        """
        Swipe the page in one direction based on screen percentage.
        Args:
            direction: 'up' | 'down' | 'left' | 'right'
            percentage: Percent of Screen to swipe: int, default is 50 means a half of screen to be scrolled
        Usage:
            - Swipe up 69% of screen:
            driver.swipe(direction = 'up', percentage = 69)
        """
        try:
            if percentage <= 0:
                percentage = 1
            percent = percentage / 100
            window_size = self._driver.get_window_size()
            if direction.lower() == "up":
                x = 0
                y = int((window_size["height"] * percent))
            if direction.lower() == "down":
                x = 0
                y = int(-(window_size["height"] * percent))
            if direction.lower() == "left":
                x = int((window_size["width"] * percent))
                y = 0
            if direction.lower() == "right":
                x = int(-(window_size["width"] * percent))
                y = 0

            self._driver.execute_script(f"window.scrollBy({x},{y})")
            logger.debug(f"Page has been scrolled {percentage}% {direction}")
            return True
        except Exception as exception:
            logger.error(exception)
            return False

    # =================================================
    # ALIAS ACTION METHODS
    # =================================================
    @gauge_wrap
    def click(self, element_locator, timeout_in_seconds: int = None):
        return self.__click(element_locator, timeout_in_seconds)

    @gauge_wrap
    def tap(self, element_locator, timeout_in_seconds: int = None):
        return self.click(element_locator, timeout_in_seconds)

    @gauge_wrap
    def type(self, element_locator, text: str, clear_first=True, timeout_in_seconds: int = None):
        return self.__type(element_locator, text, clear_first, timeout_in_seconds)

    @gauge_wrap
    def clear(self, element_locator):
        return self.__clear(element_locator)

    @gauge_wrap
    def dynamic_locator(self, based_element_locator, *sub_string):
        return self.format_locator(based_element_locator, *sub_string)

    @gauge_wrap
    def swipe_up(self, percentage: int = 50):
        """
        Swipe up the page based on screen percentage.
        Args:
            percentage: Percent of Screen to swipe: int, default is 50 means a half of screen to be scrolled
        """
        return self.swipe_page(direction="up", percentage=percentage)

    @gauge_wrap
    def swipe_down(self, percentage: int = 50):
        """
        Swipe down the page based on screen percentage.
        Args:
            percentage: Percent of Screen to swipe: int, default is 50 means a half of screen to be scrolled
        """
        return self.swipe_page(direction="down", percentage=percentage)

    @gauge_wrap
    def swipe_left(self, percentage: int = 50):
        """
        Swipe left the page based on screen percentage.
        Args:
            percentage: Percent of Screen to swipe: int, default is 50 means a half of screen to be scrolled
        """
        return self.swipe_page(direction="left", percentage=percentage)

    @gauge_wrap
    def swipe_right(self, percentage: int = 50):
        """
        Swipe right the page based on screen percentage.
        Args:
            percentage: Percent of Screen to swipe: int, default is 50 means a half of screen to be scrolled
        """
        return self.swipe_page(direction="right", percentage=percentage)

    # =================================================
    # ELEMENT ACTION JAVASCRIPT
    # =================================================

    @gauge_wrap
    def click_by_javascript(self, element_locator, timeout_in_seconds: int = None):
        timeout = max(timeout_in_seconds, 0) if timeout_in_seconds is not None else self.__DEFAULT_TIMEOUT
        if timeout <= 0:
            return False
        try:
            element = self.find_element(element_locator, timeout)
            return False if element is None else self.click_element_by_javascript(element)
        except Exception as exception:
            logger.error(exception)
            return False

    @gauge_wrap
    def click_element_by_javascript(self, element):
        try:
            self._driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as exception:
            logger.error(exception)
            return False

    @gauge_wrap
    def highlight(self, element: WebElement, border_thickness: int = 2, color: str = "red"):
        """Highlight an element
        e.g. highlight(element=open_window_elem, border_thickness=3, color="blue")"""
        try:
            if self.is_element_stale(element):
                logger.warning("The element is stale, please check it again !!!")
                return False
            parent = element._parent
            if "selenium.webdriver.chrome" in str(type(parent)):

                def apply_style(s):
                    parent.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, s)

                apply_style(f"border: {border_thickness}px dashed {color};")
                return True
        except Exception as exception:
            logger.error(exception)
            return False

    # ==================================================================================================
    #                PAGE METHODS
    # ==================================================================================================

    @gauge_wrap
    def capture_element_screenshot(self, element: WebElement):
        """
        Capture a screenshot of the element to a PNG file on your report folder.
        """
        try:
            if self.is_element_stale(element):
                logger.warning("The element is stale, please check it again !!!")
            if element is None:
                logger.warning("Cannot capture non-existed element !!!")
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
    def capture_page_screenshot(self):
        """
        Capture a screenshot of the current browsing context to a PNG file on your report folder.
        """
        try:
            data_store.suite.capture_element_screenshot = None
            Screenshots.capture_screenshot()
        except Exception as exception:
            logger.error(exception)

    @gauge_wrap
    def navigate(self, url: str, wait_for_page_loaded=True, show_log=True):
        """
        Navigate to a url in the current browser session.
        """
        try:
            if self._driver is None:
                return False
            logger.debug(f"Navigating to {url} ....!!!")
            self._driver.get(url)
            if wait_for_page_loaded:
                self.wait_for_page_loaded(show_log=show_log)
            return True
        except Exception as exception:
            logger.error(exception)
            return False

    @gauge_wrap
    def __get_current_ready_state(self):
        try:
            if self._driver is None:
                return False
            self._driver.set_script_timeout(30)
            return self._driver.execute_script("return document.readyState") if hasattr(self, "_driver") else "not found"
        except Exception as exception:
            if "not reachable" in str(exception) or "no such window" in str(exception) or "Connection refused" in str(exception):
                return "driver failed"
            if exception.__dict__.get("msg"):
                message = exception.__dict__.get("msg")
                if "script timeout" in message:
                    return "timeout"
                logger.warning(message)
                if data_store.suite.license:
                    Messages.write_message(message)
            else:
                logger.warning(exception)
                if data_store.suite.license:
                    Messages.write_message(exception)
            return "exc"
        finally:
            if self._driver is not None:
                self._driver.set_script_timeout(60)

    @gauge_wrap
    def get_current_loc(self, time_out=30):
        try:
            self._driver.execute_script('const options = { enableHighAccuracy: true, timeout: 30000, maximumAge: 0}; function success(position) { const elem = document.createElement("input"); elem.type = "hidden"; elem.id = "log_location"; elem.innerText="Loc Success: " + position.coords.latitude + "," + position.coords.longitude; document.body.appendChild(elem);}function error(err) { const elem = document.createElement("input"); elem.type = "hidden"; elem.id = "error_location"; elem.innerText = err.message; document.body.appendChild(elem);} navigator.geolocation.getCurrentPosition(success, error, options);')
            start = time.time()
            while (time.time() - start) < time_out:
                loc = self.find_element("log_location", 3, show_log=False)
                err = self.find_element("error_location", 3, show_log=False)
                if loc:
                    return loc.get_attribute("innerText")
                if err:
                    return err.get_attribute("innerText")
            return None
        except Exception:
            return None

    @gauge_wrap
    def wait_for_page_loaded(self, timeout_in_seconds: int = None, show_log=True):
        try:
            start_time = time.time()
            timeout = timeout_in_seconds if timeout_in_seconds is not None else 60
            self.update_archived_request_headers()
            if timeout <= 0:
                return False
            if self._driver is None:
                return False
            if self.wait_for_page_source_changed(5, show_log=False) > 5:
                message = f"Page {self._driver.current_url} is not loading, please check it again !!!"
                if show_log:
                    logger.warning(message)
                    if data_store.suite.license:
                        Messages.write_message(message)
                return False
            current_state = self.__get_current_ready_state()
            while time.time() - start_time <= timeout and current_state not in ["complete"]:
                current_state = self.__get_current_ready_state()
            if current_state in ["driver failed", "not found"]:
                return current_state
            elapsed_time = min(time.time() - start_time, timeout)
            if current_state == "complete":
                message = f"Page {self._driver.current_url} is loaded completely in {elapsed_time:.3f} seconds"
                if show_log:
                    logger.debug(message)
            else:
                message = f"Page {self._driver.current_url} is still {current_state} after {elapsed_time:.3f} seconds !!!"
                if show_log:
                    logger.warning(message)
            if data_store.suite.license:
                Messages.write_message(message)
        except Exception as exception:
            if type(exception).__name__ != "UnexpectedAlertPresentException":
                logger.warning(exception)
                if data_store.suite.license:
                    Messages.write_message(exception)
            else:
                logger.error(exception)

    @gauge_wrap
    def wait_for_page_changes_state(self, timeout_in_seconds: int = 30, show_log=True):
        try:
            self.update_archived_request_headers()
            if self._driver is None:
                return False
            start_time = time.time()
            if self._driver.caps.get("pageLoadStrategy").lower() != "none":
                return time.time() - start_time
            timeout = timeout_in_seconds if timeout_in_seconds is not None else 30
            if timeout <= 0:
                return 0
            first_state = self.__get_current_ready_state()
            current_state = first_state
            while time.time() - start_time <= timeout:
                current_state = self.__get_current_ready_state()
                if current_state != first_state:
                    break
            if current_state == first_state and show_log:
                message = f"Page does NOT change state over {time.time() - start_time:.3f} seconds !!!"
                logger.warning(message)
                if data_store.suite.license:
                    Messages.write_message(message)
            elif show_log:
                message = f"Page changes state in {time.time() - start_time:.3f} seconds !!!"
                logger.debug(message)
                if data_store.suite.license:
                    Messages.write_message(message)
            return time.time() - start_time
        except Exception as exception:
            logger.error(exception)
            return time.time() - start_time

    @gauge_wrap
    def wait_for_page_source_changed(self, timeout_in_seconds: int = 30, show_log=True):
        try:
            self.update_archived_request_headers()
            if self._driver is None:
                return False
            start_time = time.time()
            if self._driver.caps.get("pageLoadStrategy").lower() != "none":
                tmp = self._driver.page_source
                return time.time() - start_time
            timeout = timeout_in_seconds if timeout_in_seconds is not None else 30
            if timeout <= 0:
                return 0
            first_ps = self._driver.page_source
            while time.time() - start_time <= timeout:
                if first_ps != self._driver.page_source:
                    if show_log:
                        tmp = min((time.time() - start_time), timeout)
                        message = f"Page source has been changed after {tmp:.3f} seconds !!!"
                        logger.debug(message)
                        if data_store.suite.license:
                            Messages.write_message(message)
                    return time.time() - start_time

            if show_log:
                tmp = min((time.time() - start_time), timeout)
                message = f"Page source has not been changed after {tmp:.3f} seconds !!!"
                logger.warning(message)
                if data_store.suite.license:
                    Messages.write_message(message)

            return time.time() - start_time
        except Exception as exception:
            logger.error(exception)
            return time.time() - start_time

    @gauge_wrap
    def get_page_title(self, timeout_in_seconds: int = None):
        try:
            start_time = time.time()
            elapsed_time = time.time() - start_time
            timeout = timeout_in_seconds if timeout_in_seconds is not None else 30
            if timeout <= 0:
                return None
            while len(self._driver.title) == 0:
                elapsed_time = time.time() - start_time
                if elapsed_time >= timeout:
                    break
            return self._driver.title
        except Exception as exception:
            logger.warning(exception)
            if data_store.suite.license:
                Messages.write_message(exception)

    @gauge_wrap
    def accept_alert(self, timeout_in_seconds: int = None):
        try:
            start_time = time.time()
            elapsed_time = time.time() - start_time
            timeout = timeout_in_seconds if timeout_in_seconds is not None else 30
            if timeout <= 0:
                return None
            WebDriverWait(self._driver, timeout).until(EC.alert_is_present())
            alert = self._driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            logger.debug(f'Popup "{alert_text}" is accepted in {elapsed_time:.3f} seconds')
        except Exception as exception:
            logger.warning(exception)
            if data_store.suite.license:
                Messages.write_message(exception)

    @gauge_wrap
    def get_alert_text(self, timeout_in_seconds: int = None):
        try:
            timeout = timeout_in_seconds if timeout_in_seconds is not None else 30
            if timeout <= 0:
                return None
            WebDriverWait(self._driver, timeout).until(EC.alert_is_present())
            alert = self._driver.switch_to.alert
            return alert.text
        except Exception as exception:
            logger.warning(exception)
            if data_store.suite.license:
                Messages.write_message(exception)

    @gauge_wrap
    def refresh(self):
        try:
            self._driver.refresh()
        except Exception as exception:
            logger.warning(exception)
            if data_store.suite.license:
                Messages.write_message(exception)

    @gauge_wrap
    def back(self):
        try:
            self._driver.back()
        except Exception as exception:
            logger.warning(exception)
            if data_store.suite.license:
                Messages.write_message(exception)

    @gauge_wrap
    def forward(self):
        try:
            self._driver.forward()
        except Exception as exception:
            logger.warning(exception)
            if data_store.suite.license:
                Messages.write_message(exception)

    @gauge_wrap
    def zoom(self, percentage: int = 100):
        """
        Zoom page by percentage, default is 100%
        """
        try:
            self._driver.execute_script(f"document.body.style.zoom='{percentage}%'")
            logger.debug(f"Page has been zoomed to {percentage}%")
            return True
        except Exception as exception:
            logger.warning(exception)
            if data_store.suite.license:
                Messages.write_message(exception)
            return False

    @gauge_wrap
    def decode_qr_code(self, element_locator):
        """ """
        try:
            element = self.find_element(element_locator)
            if element is None:
                return None
            decoded_data = base64.b64decode(element.screenshot_as_base64)
            np_data = np.fromstring(decoded_data, np.uint8)
            img = cv2.imdecode(np_data, cv2.IMREAD_UNCHANGED)
            detector = cv2.QRCodeDetector()
            data, vertices_array, binary_qrcode = detector.detectAndDecode(img)
            if data == "":
                logger.warning("The QR code is invalid or so hard to be detected. Please try with another !!!")
            return data
        except Exception as exception:
            logger.warning(exception)
            if data_store.suite.license:
                Messages.write_message(exception)
            return None

    @gauge_wrap
    def get_value_from_network_request_headers(self, key="Authorization"):
        try:
            logs = self.get_network_request_headers()
            result = []
            for entry in logs:
                if entry.get(key.lower()):
                    result.append(entry.get(key.lower()))
            result = list(dict.fromkeys(result))
            if result:
                return result[0]
            else:
                return None
        except Exception as exception:
            logger.warning(exception)
            if data_store.suite.license:
                Messages.write_message(exception)
            return None

    @gauge_wrap
    def get_value_from_archived_request_headers(self, key="Authorization"):
        try:
            logs = data_store.spec.archived_headers
            result = []
            for entry in logs:
                if entry.get(key.lower()):
                    result.append(entry.get(key.lower()))
            result = list(dict.fromkeys(result))
            if result:
                return result
            else:
                return None
        except Exception as exception:
            logger.warning(exception)
            if data_store.suite.license:
                Messages.write_message(exception)
            return None

    @gauge_wrap
    def get_network_request_headers(self, method="Network.request"):
        try:
            logs = self._driver.get_log("performance")
            result = []
            for entry in logs:
                log = json.loads(entry["message"])["message"]
                if method.lower() in log["method"].lower():
                    if log.get("params"):
                        if log.get("params").get("headers"):
                            result.append(log.get("params").get("headers"))
                        if log.get("params").get("request"):
                            if log.get("params").get("request").get("headers"):
                                result.append(log.get("params").get("request").get("headers"))
            if result:
                return [dict(t) for t in {tuple(d.items()) for d in result}]
            return result
        except Exception as exception:
            logger.warning(exception)
            if data_store.suite.license:
                Messages.write_message(exception)
            return None

    @gauge_wrap
    def update_archived_request_headers(self):
        try:
            headers = self.get_network_request_headers()
            if headers:
                data_store.spec.archived_headers = data_store.spec.archived_headers + headers
                data_store.spec.archived_headers = [dict(t) for t in {tuple(d.items()) for d in data_store.spec.archived_headers}]
        except Exception as exception:
            logger.warning(exception)
            if data_store.suite.license:
                Messages.write_message(exception)
            return None


# ==================================================================================================
#                       ENTITY
# ==================================================================================================


class WebPage(BasePage):
    _driver: WebDriver
    _actions: ActionChains
    _download_directory: str
    _loc: str

    def init(driver):  # sourcery skip: instance-method-first-arg-name
        try:
            if driver is None:
                return None
            WebPage._KEY_CONTROL = Keys.COMMAND if platform.system() != "Windows" else Keys.CONTROL
            WebPage._driver: WebDriver = driver
            WebPage._actions = ActionChains(driver)
            WebPage._platform = str(driver.capabilities["platformName"]).lower()
            WebPage._download_directory = get_download_directory(driver)
        except Exception as exception:
            logger.error(exception)


class WebPage2(BasePage):
    _driver: WebDriver
    _actions: ActionChains
    _download_directory: str
    _loc: str

    def init(driver):  # sourcery skip: instance-method-first-arg-name
        try:
            if driver is None:
                return None
            WebPage2._KEY_CONTROL = Keys.COMMAND if platform.system() != "Windows" else Keys.CONTROL
            WebPage2._driver: WebDriver = driver
            WebPage2._actions = ActionChains(driver)
            WebPage2._platform = str(driver.capabilities["platformName"]).lower()
            WebPage2._download_directory = get_download_directory(driver)
        except Exception as exception:
            logger.error(exception)


class WebPage3(BasePage):
    _driver: WebDriver
    _actions: ActionChains
    _download_directory: str
    _loc: str

    def init(driver):  # sourcery skip: instance-method-first-arg-name
        try:
            if driver is None:
                return None
            WebPage3._KEY_CONTROL = Keys.COMMAND if platform.system() != "Windows" else Keys.CONTROL
            WebPage3._driver: WebDriver = driver
            WebPage3._actions = ActionChains(driver)
            WebPage3._platform = str(driver.capabilities["platformName"]).lower()
            WebPage3._download_directory = get_download_directory(driver)
        except Exception as exception:
            logger.error(exception)


def get_download_directory(driver):
    try:
        if hasattr(driver, "download_directory"):
            return driver.__dict__.get("download_directory")
    except Exception as exception:
        logger.error(exception)
        return None
