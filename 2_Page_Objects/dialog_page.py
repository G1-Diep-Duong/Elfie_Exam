from assertpy.assertpy import assert_that
from getgauge.python import continue_on_failure, data_store, step
from autocore import MobileScreen
from faker import Faker

fake = Faker("en_US")
# BUTTON_SKIP = "com.arlosoft.macrodroid:id/button_skip"
DYNAMIC_TEXT_ELEMENT = '//android.widget.CheckedTextView[@text="%s"]'
BUTTON_OK = '//android.widget.Button[@text="OK"]'
BUTTON_CANCEL = '//android.widget.Button[@text="CANCEL"]'
BUTTON_DELETE = '//*[@resource-id="com.arlosoft.macrodroid:id/select_dialog_listview"]/*[@text="Delete"]'
TEXTBOX_VARIABLE_NAME = "com.arlosoft.macrodroid:id/variable_new_variable_dialog_name"
SPINNER_VARIABLE_TYPE = "com.arlosoft.macrodroid:id/variable_new_variable_type_spinner"
ENTER_VARIABLE_DIALOG_VALUE = "com.arlosoft.macrodroid:id/enter_variable_dialog_value"
BUTTON_RADIO = '//android.widget.RadioButton[@text="%s"]'
TEXTBOX_NAME = "com.arlosoft.macrodroid:id/name"
MESSAGE_TEXT = "android:id/message"


class Dialog(MobileScreen):

    @step(["[Dialog] Tap Ok button", "[Options Dialog] Tap Ok button", "[Create New Variable Dialog] Tap Ok button", "[Local Variable Dialog] Tap Ok button"])
    def tap_ok_button(self):
        self.click(BUTTON_OK)

    @step("[Dialog] Tap Cancel button")
    def tap_cancel_button(self):
        self.click(BUTTON_CANCEL)

    @step("[Dialog] Tap Delete button")
    def tap_delete_button(self):
        self.click(BUTTON_DELETE)

    @step("[Options Dialog] Select <text> radio button")
    def select_text_radio_button(self, text):
        self.click(self.format_locator(DYNAMIC_TEXT_ELEMENT, text))

    @step("[Create New Variable Dialog] Add <type> Variable with Name <name>")
    def add_variable_with_name(self, type, name):
        self.type(TEXTBOX_VARIABLE_NAME, name)
        if not self.is_element_displayed("//android.widget.ListView", 1):
            self.click(SPINNER_VARIABLE_TYPE)
        self.click(self.format_locator(DYNAMIC_TEXT_ELEMENT, type))

    @step("[Local Variable Dialog] Input value <value>")
    def input_variable_value(self, value):
        self.type(ENTER_VARIABLE_DIALOG_VALUE, value)

    @step("[Local Variable Dialog] Select the Radio Button <value>")
    def select_radio_button_value(self, value):
        self.click(self.format_locator(BUTTON_RADIO, value))

    @step("[New Stopwatch Dialog] Input stopwatch name <stopwatch_name> in the dialog")
    def input_stopwatch_name_in_the_dialog(self, stopwatch_name):
        name = stopwatch_name
        if data_store.spec.get(stopwatch_name):
            if data_store.spec[stopwatch_name] == "random_string":
                data_store.spec[stopwatch_name] = fake.city()
            name = data_store.spec[stopwatch_name]
        self.type(TEXTBOX_NAME, name)

    # --------------- Verification Steps ---------------

    @step("[Dialog] Verify the message <text> is displayed")
    def verify_the_message_is_displayed(self, text):
        assert_that(self.get_text(MESSAGE_TEXT)).is_equal_to(text)
