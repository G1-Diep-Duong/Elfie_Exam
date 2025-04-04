# TC4: Verify that the user is able to Create/Delete Stopwatches

tags: suite1, tc04, debug

- Data test:
$ stopwatch_1 = 'random_string'
$ stopwatch_2 = 'Apple Watch'

- Required desired capabilities to add more to appium:
* [MobileCapabilities] Init new customized Mobile Capabilities for App MacroDroid

## Scenario
1 - Open the Macdroid application
* Open Macrodroid application

2 - Tap on "Stopwatches" Card
* [Dashboard Page] Tap on card "Stopwatches"

3 - Create Stopwatches 1
* [Stopwatches Page] Tap create Stopwatch button
* [New Stopwatch Dialog] Input stopwatch name "stopwatch_1" in the dialog
* [Dialog] Tap Ok button

4 - Verify the Stopwatch 1 is created
* [Stopwatches Page] Verify the Stopwatch "stopwatch_1" is created

5 - Create Stopwatches 2
* [Stopwatches Page] Tap create Stopwatch button
* [New Stopwatch Dialog] Input stopwatch name "stopwatch_2" in the dialog
* [Dialog] Tap Ok button

6 - Verify the Stopwatch 2 is created
* [Stopwatches Page] Verify the Stopwatch "stopwatch_2" is created

7 - Create Stopwatch 3 which name is the same with Stopwatch 2
* [Stopwatches Page] Tap create Stopwatch button
* [New Stopwatch Dialog] Input stopwatch name "stopwatch_2" in the dialog
* [Dialog] Tap Ok button

8 - Verify the message "A Stopwatch with that name already exists" is displayed
* [Dialog] Verify the message "A Stopwatch with that name already exists" is displayed
* [Dialog] Tap Ok button
* [Dialog] Tap Cancel button

9 - Delete the Stopwatch 1
* [Stopwatches Page] Tap on Stopwatch "stopwatch_1"
* [Dialog] Tap Delete button

10 - Verify the Stopwatch 1 is deleted
* [Stopwatches Page] Verify the Stopwatch "stopwatch_1" is deleted

11 - Delete the Stopwatch 2
* [Stopwatches Page] Tap on Stopwatch "stopwatch_2"
* [Dialog] Tap Delete button

12 - Verify the Stopwatch 2 is deleted
* [Stopwatches Page] Verify the Stopwatch "stopwatch_2" is deleted

13 - Verify Stopwatches Page displays "No stopwatches defined"
* [Stopwatches Page] Verify text "No stopwatches defined" displays