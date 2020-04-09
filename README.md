# OctoPyClient
An [OctoPrint](https://octoprint.org) client interface for small TFT touch-screen modules.

OctoPyClient can be installed on any X11 server either with or without a window-manager. It has been designed to support small displays with at least 480x320 resolution. The Adafruit PiTFT Plus 480x320 3.5" TFT+Touchscreen mounted on a Raspberry Pi 3B was the target configuration. Displays with larger resolutions such as 800x480 are compatible. Layout and size of display objects can be modified by an alternative style sheet provided by the `--style` option.

OctoPyClient may be installed (co-located) with an OctoPrint server or may be used remotely on a Linux Desktop within a window. Any system with the appropriate Python3 (>=3.6) and GTK+3 support should, in all likelyhood, work reasonalby well. Raspian Buster (Debian 10) is supported, Raspian Stretch (Python 3.5) is not.

This is currently a work-in-progress. It is actively being developed and it should not be used for any purpose other than reference. Expect to see frequent updates, changes to internal structure, work-flow and user interface aspects. Documentation and installation information will be added when a functional base-level is somewhat complete and stable.

### Opening Splash Screen

![AppStartup](doc/splash_screen.png)

### Main menu

![TopMenu](doc/idle_status.png)

#### Thanks to the following GitHub projects for code, ideas and icon images:

* OctoPrint REST API inetrface in Python by _dougbrion/OctoRest_
* Images/icons and general program flow from _mcaudros/OctoPrint-TFT_ and _Z-Bolt/OctoScreen_
