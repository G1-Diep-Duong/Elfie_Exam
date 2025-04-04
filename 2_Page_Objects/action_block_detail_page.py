from assertpy.assertpy import assert_that
from getgauge.python import continue_on_failure, data_store, step
from autocore import MobileScreen
from faker import Faker


BUTTON_ADD = "com.arlosoft.macrodroid:id/fab"
TEXTBOX_ACTION_BLOCK_NAME = "com.arlosoft.macrodroid:id/actionBlockNameText"
TEXTBOX_ACTION_BLOCK_DESCRIPTION = "com.arlosoft.macrodroid:id/description"
BUTTON_ADD_INPUT_VARIABLE = "com.arlosoft.macrodroid:id/addInputVariableButton"
BUTTON_ADD_OUTPUT_VARIABLE = "com.arlosoft.macrodroid:id/addOutputVariableButton"
BUTTON_ADD_ACTION = "com.arlosoft.macrodroid:id/addActionButton"
DYNAMIC_MACRO_EDIT_ENTRY_NAME_ELEMENT = '//*[@resource-id="com.arlosoft.macrodroid:id/macro_edit_entry_name" and @text="%s"]'
BUTTON_INPUT_COLLAPSE_EXPAND = "com.arlosoft.macrodroid:id/inputCollapseExpandButton"
BUTTON_OUTPUT_COLLAPSE_EXPAND = "com.arlosoft.macrodroid:id/outputCollapseExpandButton"
DYNAMIC_MACRO_EDIT_ENTRY_NAME_ELEMENT = '//*[@resource-id="com.arlosoft.macrodroid:id/macro_edit_entry_name" and @text="%s"]'
MACRO_EDIT_ENTRY_DETAIL_BY_NAME = DYNAMIC_MACRO_EDIT_ENTRY_NAME_ELEMENT + '/following-sibling::android.widget.TextView[@resource-id="com.arlosoft.macrodroid:id/macro_edit_entry_detail"]'
ACTIONS_LIST = '//*[@resource-id="com.arlosoft.macrodroid:id/actionsList"]'
INPUT_VAR_LIST = '//*[@resource-id="com.arlosoft.macrodroid:id/inputVarsList"]'
OUTPUT_VAR_LIST = '//*[@resource-id="com.arlosoft.macrodroid:id/outputVarsList"]'
BUTTON_ACCEPT = "com.arlosoft.macrodroid:id/acceptButton"
fake = Faker("en_US")


class ActionBlockDetailPage(MobileScreen):

    @step("[Action Blocks Detail Page] Add an action block Name")
    def add_an_action_block_name(self):
        data_store.scenario.action_block_name = fake.first_name()
        self.type(TEXTBOX_ACTION_BLOCK_NAME, data_store.scenario.action_block_name)

    @step("[Action Blocks Detail Page] Add an action block description")
    def add_an_action_block_description(self):
        data_store.scenario.action_block_description = fake.last_name()
        self.type(TEXTBOX_ACTION_BLOCK_DESCRIPTION, data_store.scenario.action_block_description)

    @step("[Action Blocks Detail Page] Tap Add button to add input variable")
    def tap_add_button_to_add_input_variable(self):
        self.click(BUTTON_ADD_INPUT_VARIABLE)

    @step("[Action Blocks Detail Page] Tap Add button to add output variable")
    def tap_add_button_to_add_output_variable(self):
        self.click(BUTTON_ADD_OUTPUT_VARIABLE)

    @step("[Action Blocks Detail Page] Tap Add Action button")
    def tap_add_action_button(self):
        self.click(BUTTON_ADD_ACTION)

    @step("[Action Blocks Detail Page] Tap Accept button")
    def tap_accept_button(self):
        self.click(BUTTON_ACCEPT)

    @step("[Action Blocks Detail Page] Select input variable <name>")
    def select_input_variable(self, name):
        INPUT_VARIABLE_NAME = self.format_locator(DYNAMIC_MACRO_EDIT_ENTRY_NAME_ELEMENT, name)
        if not self.is_element_displayed(INPUT_VARIABLE_NAME, 1):
            self.click(BUTTON_INPUT_COLLAPSE_EXPAND)
        self.click(INPUT_VARIABLE_NAME)

    @step("[Action Blocks Detail Page] Select output variable <name>")
    def select_output_variable(self, name):
        OUTPUT_VARIABLE_NAME = self.format_locator(DYNAMIC_MACRO_EDIT_ENTRY_NAME_ELEMENT, name)
        if not self.is_element_displayed(OUTPUT_VARIABLE_NAME, 1):
            self.click(BUTTON_OUTPUT_COLLAPSE_EXPAND)
        self.click(OUTPUT_VARIABLE_NAME)

    # --------------- Verification Steps ---------------
    @step("[Action Blocks Detail Page] Verify the Action <name> should show correct added value <value>")
    def verify_the_action_name_should_show_correct_added_value(self, name, value):
        assert_that(self.get_text(self.format_locator(ACTIONS_LIST + MACRO_EDIT_ENTRY_DETAIL_BY_NAME, name))).is_equal_to(value)

    @step("[Action Blocks Detail Page] Verify the Input Variable <name> should show correct added value <value>")
    def verify_the_input_variable_name_should_show_correct_added_value(self, name, value):
        assert_that(self.get_text(self.format_locator(INPUT_VAR_LIST + MACRO_EDIT_ENTRY_DETAIL_BY_NAME, name))).contains(value)

    @step("[Action Blocks Detail Page] Verify the Output Variable <name> should show correct added value <value>")
    def verify_the_output_variable_name_should_show_correct_added_value(self, name, value):
        assert_that(self.get_text(self.format_locator(OUTPUT_VAR_LIST + MACRO_EDIT_ENTRY_DETAIL_BY_NAME, name))).contains(value)
