from getgauge.python import continue_on_failure, data_store, step
from autocore.utils.browser_util import MobileCapabilities


class Configuration:

    @step("[MobileCapabilities] Init new customized Mobile Capabilities for App MacroDroid")
    def init_new_customized_capabilities_mobile(self):
        customized_capabilities = {
            "platformName": "Android",
            "appium:deviceName": "Android Test",
            "appium:automationName": "UiAutomator2",
            "appPackage": "com.arlosoft.macrodroid",
            "appWaitActivity": "com.arlosoft.macrodroid.intro.IntroActivity",
            "appium:ensureWebviewsHavePages": True,
            "appium:nativeWebScreenshot": True,
            "appium:newCommandTimeout": 3600,
            "appium:autoGrantPermissions": True,
            "unicodeKeyboard": True,
        }
        MobileCapabilities(customized_capabilities)
