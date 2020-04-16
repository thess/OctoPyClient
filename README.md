# OctoPyClient
An [OctoPrint](https://octoprint.org) client interface for small TFT touch-screen displays.

OctoPyClient can be installed on any X11 server either with or without a window-manager. It has been designed to support small displays with at least 480x320 resolution. The Adafruit PiTFT Plus 480x320 3.5" TFT+Touchscreen mounted on a Raspberry Pi 3B was the target configuration. Displays with larger resolutions such as 800x480 are compatible. Layout and size of display objects can be modified by an alternative style sheet provided by the `--style` option.

OctoPyClient may be installed (co-located) with an OctoPrint server or may be used remotely on a Linux Desktop within a window. Any system with the appropriate Python3 (>=3.6) and GTK+3 support should, in all likelihood, work reasonably well. Raspian Buster (Debian 10) is supported, Raspian Stretch (Python 3.5) is not.

This is currently a work-in-progress. It is actively being developed. Expect to see frequent updates, changes to internal structure, work-flow and user interface aspects. Documentation and installation information will be added as functional base-levels become somewhat complete and stable.

## Installation

This application is heavily dependent on GTK/GDK and touch-screen display interfaces. System requirements for installing and executing OctoPyClient include proper setup of an X11 server for your chosen display hardware and the necessary Python GTK and Cairo libraries. My recommendation is to install distribution provided Python3 libraries for GTK and Cairo rather than attempting to build them as a setup requirement. Getting the correct build dependencies for installing PyGObject and pycairo with PIP is possible, but tricky.

Setting up on Raspian and other Debian based distributions like Ubuntu, etc., the minimum release version that supports Python 3.6 or later is required. Ex: Debian 10 (Buster) or Ubuntu 18.04 (Bionic).

1) [_Optional_] Install Linux build tools

        $ sudo apt install git build-essentials pkg-config

2) X11 requirements if starting with console only system such as Raspian-Lite. This provides X11 server and all dependencies without a display-manager.

        $ sudo apt install xorg

3) Install the necessary Python3 environment and GTK+3 dependencies. This includes Python virtual environments and Cairo graphics libraries.

        $ sudo apt install python3-pip python3-dev python3-setuptools
        $ sudo apt install python3-virtualenv virtualenv
        $ sudo apt install python3-yaml python3-gi python3-gi-cairo gir1.2-gtk-3.0

#### Install to Python virtual environment (virtualenv)
        $ virtualenv --python=python3 --system-site-packages OctoPyClient
        $ source OctoPyClient/bin/activate
        $ pip install pip --upgrade
        $ pip install --no-cache-dir octopyclient
        --or-- If using pypi testing repo ---
        $ pip install --index-url https://test.pypi.org/simple/ --no-cache-dir --no-deps octopyclient


#### Install from source
        $ git clone https://github.com/thess/OctoPyClient
        $ cd OctoPyClient
        $ virtualenv --python=python3 --system-site-packages venv
        $ source venv/bin/activate
        $ python3 setup.py clean --all       # Only if upgrading
        $ python3 setup.py install

#### Install Debian package
*Not complete yet - TBD*

#### Systemd service configuration
See example files in the `service_files` directory to install OctoPyClient as the display_manager service for graphical_target startup. It may also be necessary to set the default startup target after enabling `octopyclient.service`, Ex:

        $ systemctl enable octopyclient.service
        $ systemctl set-default graphical.target

Client launch location, display target and command-line options can be specified by modifying the environment file located in `/etc/octopyclient.env`.

## Command line options

        $ octopyclient --help
        OctoPyClient (0.9.12) - Touchscreen client for OctoPrint

            octopyclient [opts] [server]

        Hostname or IP of OctoPrint server installation (default: localhost:5000)

        Command-line opts:

        -h, --help        This text
        -l, --loglevel    Log verbosity [DEBUG, INFO, WARNING, etc.] level (default: WARNING)
        -f, --log         Log file path (default: stdout)
        -k, --key         Octoprint API key (mandatory)
        -s, --style       Location of CSS style sheet (default: style.css)
        -r, --resolution  Screen resolution (default: 480x320)
        -c, --config      Location of Octoprint configuration (default: $HOME/.octoprint/config.yaml)
        -p, --preset      Default temperature preset from OctoPrint (default: PLA)
            --noblank     Disable DPMS and screen-saver blanking


### Main menu

![idle_status](https://raw.githubusercontent.com/thess/octopyclient/master/doc/images/idle_status.png)

#### Thanks to the following GitHub projects for code, ideas and icon images:

* OctoPrint REST API interface in Python by _dougbrion/OctoRest_
* Images/icons and general program flow from _mcaudros/OctoPrint-TFT_ and _Z-Bolt/OctoScreen_
