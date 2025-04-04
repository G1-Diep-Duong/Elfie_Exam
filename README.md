# Gauge Test Automation Framework Setup (Python, macOS)

For this assignment, use this guide to set up the Gauge test automation framework with Python on macOS.

## Prerequisites

* **Homebrew:** If not already installed, install Homebrew:
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
* **Python:** Ensure Python 3 is installed. You can install it via Homebrew:
    ```bash
    brew install python3
    ```
* **Pip:** Check Python's package installer for this assignment:

    ```bash
    pip3 --version
    ```

## Step 1: Install Gauge

1.  **Install Gauge using Homebrew:**
    ```bash
    brew install gauge
    ```
2.  **Verify installation:**
    ```bash
    gauge --version
    ```

## Step 2: Install Gauge Python Plugin

1.  **Install the Gauge Python plugin:**
    ```bash
    gauge install python
    ```
2.  **Verify plugin installation:**
    ```bash
    gauge version
    ```
    You should see the Python plugin listed.

## Step 3: Install Dependencies

1.  **Install dependencies using pip:**
    - Navigate to project folder:
    ```bash
    pip3 install -r requirements.txt
    ```
    If you don't have a requirements.txt file, you can install packages individually.

# Setting up Android Device for Appium on macOS

This guide outlines the steps to set up an Android device for Appium testing on macOS.

## Prerequisites

* **macOS:** A macOS machine.
* **Android Device:** A physical Android device or an Android emulator.
* **Java Development Kit (JDK):** Ensure JDK is installed.
* **Android SDK:** Install the Android SDK.
* **Node.js and npm:** Install Node.js and npm (Node Package Manager).
* **Appium Server:** Install Appium.
* **Appium Doctor:** (Optional, but recommended) Install Appium Doctor to verify your setup.
* **USB Cable (for physical device):** If testing on a physical device.

## Step 1: Install Java Development Kit (JDK)

1.  **Download JDK:** Download the latest JDK from Oracle or Adoptium (Eclipse Temurin).
2.  **Install JDK:** Follow the installation instructions for your downloaded JDK.
3.  **Verify Installation:** Open Terminal and run:
    ```bash
    java -version
    javac -version
    ```
    This should display the installed Java and compiler versions.

## Step 2: Install Android SDK

1.  **Download Android Studio:** Download Android Studio from the official Android Developer website.
2.  **Install Android Studio:** Follow the installation instructions. During installation, Android Studio will install the Android SDK.
3.  **Configure Android SDK:**
    * Open Android Studio.
    * Go to **Configure > SDK Manager**.
    * Install the desired Android SDK platforms (e.g., Android 13.0 (Tiramisu)).
    * Install **Android SDK Platform-Tools** and **Android SDK Build-Tools**.
    * Note the **Android SDK Location** path, as it will be needed later.
4.  **Set Environment Variables:**
    * Open your `.bash_profile`, `.zshrc`, or equivalent shell configuration file.
    * Add the following lines, replacing `/path/to/android/sdk` with your actual Android SDK location:
        ```bash
        export ANDROID_HOME=/path/to/android/sdk
        export PATH=$PATH:$ANDROID_HOME/platform-tools
        export PATH=$PATH:$ANDROID_HOME/tools
        export PATH=$PATH:$ANDROID_HOME/build-tools/<desired build tool version>
        ```
    * Example using zsh:
        ```bash
        export ANDROID_HOME=/Users/yourusername/Library/Android/sdk
        export PATH=$PATH:$ANDROID_HOME/platform-tools
        export PATH=$PATH:$ANDROID_HOME/tools
        export PATH=$PATH:$ANDROID_HOME/build-tools/33.0.2
        ```
    * Apply the changes by running:
        ```bash
        source ~/.zshrc # or source ~/.bash_profile
        ```
    * Verify the variables:
        ```bash
        echo $ANDROID_HOME
        adb version
        ```

## Step 3: Install Node.js and npm

1.  **Download Node.js:** Download the latest LTS version of Node.js from the official Node.js website.
2.  **Install Node.js:** Follow the installation instructions.
3.  **Verify Installation:** Open Terminal and run:
    ```bash
    node -v
    npm -v
    ```
    This should display the installed Node.js and npm versions.

## Step 4: Install Appium Server

1.  **Install Appium:** Run the following command in Terminal:
    ```bash
    npm install -g appium
    ```
2.  **Verify Installation:** Run:
    ```bash
    appium -v
    ```

## Step 5: Install Appium Doctor (Optional)

1.  **Install Appium Doctor:** Run:
    ```bash
    npm install -g appium-doctor
    ```
2.  **Run Appium Doctor:** Run:
    ```bash
    appium-doctor
    ```
    Appium Doctor will check your environment and provide recommendations for any missing dependencies.

## Step 6: Configure Android Device

### Physical Device

1.  **Enable Developer Options:**
    * Go to **Settings > About phone**.
    * Tap **Build number** seven times until you see "You are now a developer!".
2.  **Enable USB Debugging:**
    * Go to **Settings > System > Developer options**.
    * Enable **USB debugging**.
3.  **Connect Device:** Connect your Android device to your macOS machine using a USB cable.
4.  **Authorize USB Debugging:** On your Android device, allow USB debugging when prompted.
5.  **Verify Device Connection:** Run:
    ```bash
    adb devices
    ```
    This should display your connected device.

### Android Emulator

1.  **Create Emulator:**
    * Open Android Studio.
    * Go to **Tools > Device Manager**.
    * Click **Create Virtual Device**.
    * Select a device definition and system image.
    * Click next and then finish.
2.  **Start Emulator:**
    * From the device manager, click the green play button next to the created emulator.
3.  **Verify Emulator Connection:** Run:
    ```bash
    adb devices
    ```
    This should display your running emulator.

# Run Your Gauge Tests 

## A - Run Your Gauge Tests with specific Mobile device

1.  **Run specifications with specific Mobile device:**
    ```bash
    gauge run -v -t "udid:emulator-5554|tc01"
    ```
    - The test cases which have tag "__tc01__" will be executed with mobile which has udid __emulator-5554__

For more detail: [Run Gauge Specifications](https://docs.gauge.org/execution.html?os=macos&language=python&ide=vscode)

2.  **View the Gauge report:**
    * Gauge generates an HTML report in the `reports` directory.
    * Open `reports/html-report/yyyy-mm-dd_hh.MM.ss/index.html` in your browser.

## B - Run parallel tests on mobile devices
- e.g. Achieve parallel execution across three devices by launching each CLI command in distinct terminal sessions.:
    
    ```bash
    gauge run -v -t "udid:emulator-5554|tc02_3_times" 
    ```
    
    ```bash
    gauge run -v -t "udid:emulator-5556|tc01_3_times"
    ```
    
    ```bash
    gauge run -v -t "udid:emulator-5558|tc03|tc04"
    ```
## C - [Integration with CI/CD](https://docs.gauge.org/examples?os=macos&language=python&ide=vscode#integration-with-ci-cd)


## D - Additional Configuration

* **Gauge Plugins:** Explore other Gauge plugins for specific functionality (e.g., reporting, database testing).
* **Gauge Properties:** Customize Gauge behavior using the `env/default/default.properties` file.

## E - Troubleshooting

* **Plugin Issues:** If you encounter plugin-related issues, try reinstalling the plugin.
* **Dependency Problems:** Ensure all required dependencies are installed correctly.
* **Gauge Errors:** Refer to the [Gauge documentation](https://docs.gauge.org/troubleshooting?os=macos&language=python&ide=vscode) for error messages and solutions.

This guideline should help you set up and run your Gauge test automation framework with Python on macOS.