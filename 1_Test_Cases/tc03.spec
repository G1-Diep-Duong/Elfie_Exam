# TC3: Verify that the user is able to search in System Log

tags: suite1, tc03

- Required desired capabilities to add more to appium:
* [MobileCapabilities] Init new customized Mobile Capabilities for App MacroDroid

- Data driven test:
$ valid_key_search = ['Mac','droid','screen','attempting', 'service created']
$ invalid_key_search = ['Not Exist','Invalid']

## Scenario
1 - Open the Macdroid application
* Open Macrodroid application

2 - Tap on System Log Card
* [Dashboard Page] Tap on card "System Log"

3 - System Log Page] Set log level to "Detailed"
* [System Log Page] Set log level to "Detailed"

4 - [System Log Page] Verify Search log contains key when searching key which occurs in the log
* [System Log Page] Verify Search log contains key for data driven test "valid_key_search"

5 - [System Log Page] Verify Search log displays empty when searching key which not in the log
* [System Log Page] Verify Search log is empty for data driven test "invalid_key_search"
