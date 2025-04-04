# TC2: Verify that the user is able to add an action block

tags: suite1, tc02

- Required desired capabilities to add more to appium:
* [MobileCapabilities] Init new customized Mobile Capabilities for App MacroDroid

## Scenario
1 - Open the Macdroid application
* Open Macrodroid application

2 - Tap on Action Blocks Menu
* [Dashboard Page] Tap on card "Action Blocks"

3 - On Action Blocks Page, Tap on Add button
* [Action Blocks Page] Tap on Add button

4 - On Action Blocks Detail Page, add an action block Name
* [Action Blocks Detail Page] Add an action block Name

5 - Add a action block description
* [Action Blocks Detail Page] Add an action block description

6 - On Action Block Detail Page, Add on a input variable name
7 - Add Boolean value and ok
* [Action Blocks Detail Page] Tap Add button to add input variable
* [Create New Variable Dialog] Add "Boolean" Variable with Name "Diep_Input"
* [Create New Variable Dialog] Tap Ok button

8 - Select new added input variable
* [Action Blocks Detail Page] Select input variable "Diep_Input"

9 - Select the Value to True
* [Local Variable Dialog] Select the Radio Button "True"
* [Local Variable Dialog] Tap Ok button

10 - On Action Blocks Detail Page, tap on Action to add an action
11 - On Action page, tap on Logging
12 - Select Clear Log
13 - Select System Log and OK
* [Action Blocks Detail Page] Tap Add Action button
* [Add Action Page] Tap on category "Logging"
* [Add Action Page] Tap on item "Clear Log"
* [Options Dialog] Select "System Log" radio button
* [Options Dialog] Tap Ok button

14 - On Action Block Detail Page, Add on a out variable name
15 - Add String value and ok
16 - Select new added output variable
17 - Add String value = “This is a testing string”
* [Action Blocks Detail Page] Tap Add button to add output variable
* [Create New Variable Dialog] Add "String" Variable with Name "Duong_Output"
* [Create New Variable Dialog] Tap Ok button
* [Action Blocks Detail Page] Select output variable "Duong_Output"
* [Local Variable Dialog] Input value "This is a testing string"
* [Local Variable Dialog] Tap Ok button

18 - Verify information display in Action Block detail page
* [Action Blocks Detail Page] Verify the Input Variable "Diep_Input" should show correct added value "True"
* [Action Blocks Detail Page] Verify the Action "Clear Log" should show correct added value "System Log"
* [Action Blocks Detail Page] Verify the Output Variable "Duong_Output" should show correct added value "This is a testing string"

19 - Tap on “V” button to add the action block
* [Action Blocks Detail Page] Tap Accept button

20 - In Action Block Page, verify the block name and action block description
* [Action Blocks Page] Verify the action block name and action block description should show correct

