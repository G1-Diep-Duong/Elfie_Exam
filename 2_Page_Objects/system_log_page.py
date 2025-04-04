from assertpy.assertpy import assert_that, soft_assertions
from getgauge.python import continue_on_failure, data_store, step, Messages
from autocore import MobileScreen

BUTTON_FILTER = "com.arlosoft.macrodroid:id/menu_filter"
SPINNER_LOG_LEVEL = "com.arlosoft.macrodroid:id/logLevelSpinner"
DYNAMIC_OPTION = '//android.widget.ListView/*[@text="%s"]'
BUTTON_SEARCH = "com.arlosoft.macrodroid:id/search_button"
TEXTBOX_SEARCH = "com.arlosoft.macrodroid:id/search_src_text"
FLIPPER_VIEW = "com.arlosoft.macrodroid:id/viewFlipper"
DYNAMIC_TEXT = '//android.widget.TextView[@text="%s"]'
LOG_TEXT = '//android.widget.TextView[@resource-id="com.arlosoft.macrodroid:id/logText"]'


class SystemLogPage(MobileScreen):

    @step("[System Log Page] Set log level to <log_type>")
    def set_log_level(self, log_type):
        if not self.is_element_displayed(SPINNER_LOG_LEVEL, 1):
            self.tap_on_filter_button()
        self.click(SPINNER_LOG_LEVEL)
        self.click(self.format_locator(DYNAMIC_OPTION, log_type))

    @step("[System Log Page] Search log for text <text>")
    def search_log(self, text):
        if not self.is_element_displayed(TEXTBOX_SEARCH, 1):
            self.tap_on_search_button()
        self.type(TEXTBOX_SEARCH, text)

    # --------------- Verification Steps ---------------

    @continue_on_failure
    @step("[System Log Page] Verify Search log contains key for data driven test <key_search>")
    def verify_search_log_contains_key(self, key_search):
        keys = data_store.spec.get(key_search)
        with soft_assertions():
            for key in keys:
                self.search_log(key)
                result = self.get_log_texts()
                if not result:
                    Messages.write_message(f"Search log for '{key}' is empty !!!")
                    assert_that(result).is_not_empty()
                else:
                    for item in result:
                        Messages.write_message(f"Verify Search key '{key}' displays in log line '{item}'")
                        assert_that(item.lower()).contains(key.lower())

    @continue_on_failure
    @step("[System Log Page] Verify Search log is empty for data driven test <key_search>")
    def verify_search_log_empty(self, key_search):
        keys = data_store.spec.get(key_search)
        with soft_assertions():
            for key in keys:
                self.search_log(key)
                assert_that(self.is_element_displayed(self.format_locator(DYNAMIC_TEXT, "No events logged"))).is_true()

    # --------------- Page Method ---------------

    def tap_on_filter_button(self):
        self.click(BUTTON_FILTER)

    def tap_on_search_button(self):
        self.click(BUTTON_SEARCH)

    def get_log_texts(self):
        sub_element_texts = []
        elements = self.find_elements(LOG_TEXT, 3)
        if elements:
            sub_element_texts = [element.text for element in elements if element.text]
        return sub_element_texts
