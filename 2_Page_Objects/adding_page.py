from assertpy.assertpy import assert_that
from getgauge.python import continue_on_failure, data_store, step
from autocore import MobileScreen

DYNAMIC_TEXT_CATEGORY = '//*[@resource-id="com.arlosoft.macrodroid:id/category_name" and @text="%s"]'
DYNAMIC_TEXT_ITEM = '//android.widget.TextView[@resource-id="com.arlosoft.macrodroid:id/select_item_name" and @text="%s"]'

class AddingPage(MobileScreen):
    
    @step(["[Add Action Page] Tap on category <text>","[Add Trigger Page] Tap on category <text>","[Add Constraint Page] Tap on category <text>"])
    def tap_on_category(self, text):
        self.click(self.format_locator(DYNAMIC_TEXT_CATEGORY, text))

    @step(["[Add Action Page] Tap on item <text>","[Add Trigger Page] Tap on item <text>","[Add Constraint Page] Tap on item <text>"])
    def tap_on_item(self, text):
        self.click(self.format_locator(DYNAMIC_TEXT_ITEM, text))