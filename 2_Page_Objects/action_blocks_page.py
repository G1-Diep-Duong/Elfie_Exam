from assertpy.assertpy import assert_that
from getgauge.python import continue_on_failure, data_store, step
from autocore import MobileScreen

BUTTON_ADD = "com.arlosoft.macrodroid:id/fab"
NAME = "com.arlosoft.macrodroid:id/name"
DESCRIPTION = "com.arlosoft.macrodroid:id/description"


class ActionBlocksPage(MobileScreen):

    @step("[Action Blocks Page] Tap on Add button")
    def tap_on_add_button(self):
        self.click(BUTTON_ADD)

    # --------------- Verification Steps ---------------
    @step("[Action Blocks Page] Verify the action block name and action block description should show correct")
    def verify_name_and_description_should_show_correct(self):
        assert_that(self.get_text(NAME)).is_equal_to(data_store.scenario.action_block_name)
        assert_that(self.get_text(DESCRIPTION)).is_equal_to(data_store.scenario.action_block_description)
