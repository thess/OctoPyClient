#!/usr/bin/env python3

"""
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

"""

__version__ = "0.9.14"

import sys
import os
import getopt
import logging
import yaml

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from .ui import UI
from .utils import getStylePath, setStyleBase
from .common import Config

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

HOMEPI = "/home/pi/"
CONFIGFILE = ".octoprint/config.yaml"

def findConfigFile():
    file = doFindConfigFile(HOMEPI)
    if file is not None:
        return file

    usr = os.path.expanduser('~')
    if usr is None:
        return None

    return doFindConfigFile(usr)

def doFindConfigFile(base):
    path = os.path.join(base, CONFIGFILE)
    try:
        os.stat(path)
    except FileNotFoundError:
        return None

    return path

def readConfigFile(configFile, cfg):
    if configFile is None:
        return
    try:
        with open(configFile, 'r') as f:
            try:
                yml = yaml.safe_load(f)
            except yaml.YAMLError as err:
                eprint("Error parsing: ({}) {}".format(configFile, str(err)))
                return
    except Exception as err:
        raise Usage("Cannot read config file: {}".format(str(err)))

    # Extract items - ignore missing (will use defaults)
    # Items can be overridden by command-line options
    try:
        cfg.host = yml['server']['host']
    except (AttributeError, KeyError):
        pass

    try:
        cfg.port = yml['server']['port']
    except (AttributeError, KeyError):
        pass

    try:
        cfg.api_key = yml['api']['key']
    except (AttributeError, KeyError):
        pass

    return

def main(argv=None):
    # Parse any command-line args
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hl:f:k:s:r:c:p:", ["help", "loglevel=", "log=", "key=",
                                                                "style=", "resolution=", "config=", "preset="])
        except getopt.error as msg:
            raise Usage(msg)

        # Gather command options
        loglevel = logging.WARNING
        logfile = None
        style_sheet = getStylePath("style.css")

        # OctoPrint config defaults
        cfg = Config(api_key=None, host="localhost", port=5000,
                     width=480, height=320, preset="PLA")

        # Find and parse possible local OctoPrint config file
        octoprintConfig = findConfigFile()
        if octoprintConfig is not None:
            readConfigFile(octoprintConfig, cfg)

        # Options may override config items
        for o, v in opts:
            if o in ['-h', '--help']:
                print("OctoPrint ({:s}) touchscreen client".format(__version__))
                print(__doc__)
                return

            if o in ['-f', '--log']:
                logfile = v
            elif o in ['-l', '--loglevel']:
                loglevel = getattr(logging, v.upper())
            elif o in ['-k', '--key']:
                cfg.api_key = v
            elif o in ['-s', '--style']:
                setStyleBase(v)
            elif o in ['-r', '--resolution']:
                try:
                    size = v.split('x')
                    cfg.width = int(size[0])
                    cfg.height = int(size[1])
                except:
                    raise Usage("Screen resolution invalid")
            elif o in ['-c', '--config']:
                readConfigFile(v, cfg)
            elif o in ['-p', '--preset']:
                cfg.profile = v

        # Remaining arg is octoprint host
        if len(args) == 1:
            hostURL = args[0]
        else:
            hostURL = "http://{:s}:{:d}".format(cfg.host, cfg.port)

        if cfg.api_key is None:
            raise Usage("Octoprint API key required")

        try:
            logfmt = '%(asctime)s.%(msecs)03d  OctoPyClient%(levelname)8s %(filename)s:%(lineno)d - %(message)s'
            logtime = '%H:%M:%S'
            # Set root logger level default to ERROR. Set to WARNING when DEBUG requested.
            rootLoglevel = logging.WARNING if loglevel == logging.DEBUG else logging.ERROR
            if not logfile:
                logging.basicConfig(level=rootLoglevel, stream=sys.stdout, format=logfmt, datefmt=logtime)
            else:
                logging.basicConfig(level=rootLoglevel, filename=logfile, filemode='w', format=logfmt, datefmt=logtime)
            # Custom global logger - set level
            logging.getLogger('OctoPyClient').setLevel(loglevel)

            Gtk.init()
            settings = Gtk.Settings.get_default()
            settings.set_property("gtk_application_prefer_dark_theme", True)

            ui = UI(hostURL, cfg, style_sheet)

            ui.show_all()
            ui.n.notify('READY=1')

            Gtk.main()

        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            if exc_type == KeyboardInterrupt:
                if ui is not None:
                    ui.Quit()
                return 0
            logging.exception("Caught network or other error:")

    except Usage as err:
        eprint("OctoPyClient ({:s}) - Touchscreen client for OctoPrint\n".format(__version__))
        eprint(err.msg)
        eprint("for help use --help")
        return 2

    finally:
        logging.shutdown()
        return
