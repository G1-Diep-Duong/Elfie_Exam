from assertpy.assertpy import assert_that
from getgauge.python import continue_on_failure, data_store, step
from autocore import MobileScreen

DYNAMIC_TEXT_CARD = '//*[@resource-id="com.arlosoft.macrodroid:id/title" and @text="%s"]'


class DashboardPage(MobileScreen):

    @step("[Dashboard Page] Tap on card <text>")
    def tap_on_card_text(self, text):
        CARD_LOCATOR = self.format_locator(DYNAMIC_TEXT_CARD, text)
        if not self.is_element_displayed(CARD_LOCATOR, 1):
            self.swipe_up()
        self.click(CARD_LOCATOR)
