from assertpy.assertpy import assert_that
from getgauge.python import continue_on_failure, data_store, step
from autocore import MobileScreen

BUTTON_ADD_TRIGGER = "com.arlosoft.macrodroid:id/edit_macro_addTriggerButton"
BUTTON_ADD_ACTION = "com.arlosoft.macrodroid:id/edit_macro_addActionButton"
BUTTON_ADD_CONSTRAINT = "com.arlosoft.macrodroid:id/edit_macro_addConstraintButton"
TEXT_LOCAL_VARIABLE = "com.arlosoft.macrodroid:id/localVarsLabel"
BUTTON_ADD_LOCAL_VARIABLE = "com.arlosoft.macrodroid:id/addVariableButton"
DYNAMIC_MACRO_EDIT_ENTRY_NAME_ELEMENT = '//*[@resource-id="com.arlosoft.macrodroid:id/macro_edit_entry_name" and @text="%s"]'
MACRO_EDIT_ENTRY_DETAIL_BY_NAME = DYNAMIC_MACRO_EDIT_ENTRY_NAME_ELEMENT + '/following-sibling::android.widget.TextView[@resource-id="com.arlosoft.macrodroid:id/macro_edit_entry_detail"]'
TRIGGERS_LIST = '//*[@resource-id="com.arlosoft.macrodroid:id/triggersList"]'
ACTIONS_LIST = '//*[@resource-id="com.arlosoft.macrodroid:id/actionsList"]'
CONSTRAINTS_LIST = '//*[@resource-id="com.arlosoft.macrodroid:id/constraintsList"]'


class MacroPage(MobileScreen):

    @step("[Macro Page] Tap on Triggers to add a trigger")
    def tap_on_add_trigger(self):
        self.click(BUTTON_ADD_TRIGGER)

    @step("[Macro Page] Tap on Actions to add an action")
    def tap_on_add_action(self):
        self.click(BUTTON_ADD_ACTION)

    @step("[Macro Page] Tap on Constraints to add a constraint")
    def tap_on_add_constraint(self):
        self.click(BUTTON_ADD_CONSTRAINT)

    @step("[Macro Page] Select add Local Variable")
    def select_add_local_variable(self):
        if not self.is_element_displayed(BUTTON_ADD_LOCAL_VARIABLE, 1):
            self.click(TEXT_LOCAL_VARIABLE)
        self.click(BUTTON_ADD_LOCAL_VARIABLE)

    @step("[Macro Page] Select new added Local Variable <name>")
    def select_new_added_local_variable_by_name(self, name):
        self.click(self.format_locator(DYNAMIC_MACRO_EDIT_ENTRY_NAME_ELEMENT, name))

    # --------------- Verification Steps ---------------
    @step("[Macro Page] Verify the Trigger <name> should show correct added value <value>")
    def verify_the_trigger_name_should_show_correct_added_value(self, name, value):
        assert_that(self.get_text(self.format_locator(TRIGGERS_LIST + MACRO_EDIT_ENTRY_DETAIL_BY_NAME, name))).is_equal_to(value)

    @step("[Macro Page] Verify the Action <name> should show correct added value <value>")
    def verify_the_action_name_should_show_correct_added_value(self, name, value):
        assert_that(self.get_text(self.format_locator(ACTIONS_LIST + MACRO_EDIT_ENTRY_DETAIL_BY_NAME, name))).is_equal_to(value)

    @step("[Macro Page] Verify the Constraint <name> should show correct")
    def verify_the_constraint_name_should_show_correct(self, name):
        assert_that(self.get_text(self.format_locator(CONSTRAINTS_LIST + DYNAMIC_MACRO_EDIT_ENTRY_NAME_ELEMENT, name))).is_equal_to(name)

    @step("[Macro Page] Verify the Local Variable <name> should show correct added value <value>")
    def verify_the_local_variable_name_should_show_correct_added_value(self, name, value):
        assert_that(self.get_text(self.format_locator(MACRO_EDIT_ENTRY_DETAIL_BY_NAME, name))).is_equal_to(value)
