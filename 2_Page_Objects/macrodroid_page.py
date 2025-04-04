from assertpy.assertpy import assert_that
from getgauge.python import continue_on_failure, data_store, step
from autocore import MobileScreen

BUTTON_SKIP = "com.arlosoft.macrodroid:id/button_skip"
BUTTON_NAVIGATE_UP = '//android.widget.ImageButton[@content-desc="Navigate up"]'


class MacrodroidPage(MobileScreen):

    @step("Open Macrodroid application")
    def open_application(self):
        self._adb.clear_data("com.arlosoft.macrodroid")
        self._driver.activate_app("com.arlosoft.macrodroid")
        if self.is_element_displayed(BUTTON_SKIP, 3):
            self.click(BUTTON_SKIP)
            self.click(BUTTON_NAVIGATE_UP)
        # self._driver.execute_script("mobile: startActivity", {"package": "com.arlosoft.macrodroid", "activity": ".homescreen.NewHomeScreenActivity"})

