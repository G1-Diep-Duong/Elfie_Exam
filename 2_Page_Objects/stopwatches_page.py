from assertpy.assertpy import assert_that, fail
from getgauge.python import continue_on_failure, data_store, step, Messages
from autocore import MobileScreen
from faker import Faker

fake = Faker("en_US")
BUTTON_ADD = "com.arlosoft.macrodroid:id/fab"
DYNAMIC_STOPWATCH_NAME = '//*[@resource-id="com.arlosoft.macrodroid:id/stopwatch_name" and @text="%s"]'
DYNAMIC_TEXT = '//android.widget.TextView[@text="%s"]'


class StopwatchesPage(MobileScreen):

    @step("[Stopwatches Page] Tap create Stopwatch button")
    def tap_create_stopwatch_button(self):
        self.click(BUTTON_ADD)

    @step("[Stopwatches Page] Tap on Stopwatch <stopwatch_name>")
    def tap_on_stopwatch(self, stopwatch_name):
        name = data_store.spec.get(stopwatch_name) if data_store.spec.get(stopwatch_name) else stopwatch_name
        self.click(self.format_locator(DYNAMIC_STOPWATCH_NAME, name))

    # --------------- Verification Steps ---------------
    @continue_on_failure
    @step("[Stopwatches Page] Verify the Stopwatch <stopwatch_name> is created")
    def verify_the_stopwatch_is_created(self, stopwatch_name):
        name = data_store.spec.get(stopwatch_name) if data_store.spec.get(stopwatch_name) else stopwatch_name
        assert_that(self.is_element_displayed(self.format_locator(DYNAMIC_STOPWATCH_NAME, name))).is_true()

    @continue_on_failure
    @step("[Stopwatches Page] Verify the Stopwatch <stopwatch_name> is deleted")
    def verify_the_stopwatch_is_deleted(self, stopwatch_name):
        name = data_store.spec.get(stopwatch_name) if data_store.spec.get(stopwatch_name) else stopwatch_name
        assert_that(self.is_element_displayed(self.format_locator(DYNAMIC_STOPWATCH_NAME, name), 1)).is_false()

    @continue_on_failure
    @step("[Stopwatches Page] Verify text <text> displays")
    def verify_text_displays(self, text):
        assert_that(self.is_element_displayed(self.format_locator(DYNAMIC_TEXT, text))).is_true()
