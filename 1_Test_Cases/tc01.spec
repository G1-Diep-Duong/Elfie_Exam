# TC1: Verify that the user is able to add a macro (don’t need to add macro name) (add 1 macro)

tags: suite1, tc01

- Required desired capabilities to add more to appium:
* [MobileCapabilities] Init new customized Mobile Capabilities for App MacroDroid

## Scenario
1 - Open Macrodroid application
* Open Macrodroid application

2 - On Dashboard Page, tap on click Macro
* [Dashboard Page] Tap on card "Add Macro"

3 - On Macro Page, tap on Trigger to add a trigger
* [Macro Page] Tap on Triggers to add a trigger

4 - On Trigger Page, tap on Application
* [Add Trigger Page] Tap on category "Applications"

5 - Tap on App Install/Remove/Update
* [Add Trigger Page] Tap on item "App Install/Remove/Update"

6 - Select Application Removed radio button
* [Options Dialog] Select "Application Removed" radio button
* [Options Dialog] Tap Ok button

7 - Select Any Application and OK
* [Options Dialog] Select "Any Application" radio button
* [Options Dialog] Tap Ok button

- Verify The Trigger Macro should show correct added values
* [Macro Page] Verify the Trigger "Application Removed" should show correct added value "Any Application"

8 - On Macro Page, tap on Action to add an action
* [Macro Page] Tap on Actions to add an action

9 - On Action page, tap on Logging
* [Add Action Page] Tap on category "Logging"

10 - Select Clear Log
* [Add Action Page] Tap on item "Clear Log"

11 - Select System Log and OK
* [Options Dialog] Select "System Log" radio button
* [Options Dialog] Tap Ok button

- Verify The Action Macro should show correct added values
* [Macro Page] Verify the Action "Clear Log" should show correct added value "System Log"

12 - On Macro Page, tap on Constrains to add an contrains
* [Macro Page] Tap on Constraints to add a constraint

13 - Select Device State
* [Add Constraint Page] Tap on category "Device State"

14 - Select Airplan Mode
* [Add Constraint Page] Tap on item "Airplane Mode"

15 - Select Airplan Mode Disable and OK
* [Options Dialog] Select "Airplane Mode Disabled" radio button
* [Options Dialog] Tap Ok button

- Verify The Constraint Macro should show correct
* [Macro Page] Verify the Constraint "Airplane Mode Disabled" should show correct

16 - On Macro Page, select add Local Variable
* [Macro Page] Select add Local Variable

17 - Add an Interger Variable with Name “Test Case”
* [Create New Variable Dialog] Add "Integer" Variable with Name "Test Case"
* [Create New Variable Dialog] Tap Ok button

18 - Select new added Variable, and input Value 1
* [Macro Page] Select new added Local Variable "Test Case"
* [Local Variable Dialog] Input value "1"
* [Local Variable Dialog] Tap Ok button

- Verify the Local Variable "Test Case" should show correct added value "1"
* [Macro Page] Verify the Local Variable "Test Case" should show correct added value "1"
