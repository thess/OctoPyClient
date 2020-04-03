#!/usr/bin/env python3

""" OctoPyClient [opts] [server]

Hostname or IP of OctoPrint server installation (default: localhost:5000)

Command-line opts:

-h, --help      This text
-l, --loglevel  Specify log verbosity level (INFO, WARN, etc.)
-f, --log       Specify log file (default stdout)
-k, --key       Octoprint API key (mandatory)
-s, --style     Location of CSS style sheet (default: style.css)
-l, --layout    Screen resolution (default: 480x320)
-c, --config    Location of Octoprint configuration (default: $HOME/.octoprint/config.yaml)

"""

__version__ = "0.9.8"

import sys
import os
import getopt
import logging
import yaml

from attr import dataclass

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from .ui import UI
from .utils import getStylePath, setStyleBase

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

HOMEPI = "/home/pi/"
CONFIGFILE = ".octoprint/config.yaml"

@dataclass
class config:
    api_key:    str
    host:       str
    port:       int

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
            opts, args = getopt.getopt(argv[1:], "hl:f:k:s:r:c:", ["help", "loglevel=", "log=", "key=",
                                                                "style=", "resolution=", "config="])
        except getopt.error as msg:
            raise Usage(msg)

        # Gather command options
        loglevel = logging.WARNING
        logfile = None
        width = 480
        height = 320
        style_sheet = getStylePath("style.css")

        # OctoPrint config defaults
        cfg = config(None, "localhost", 5000)

        # Find and parse possible local OctoPrint config file
        octoprintConfig = findConfigFile()
        if octoprintConfig is not None:
            readConfigFile(octoprintConfig, cfg)

        # Options may override config items
        for o, v in opts:
            if o in ['-h', '--help']:
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
                    width = int(size[0])
                    height = int(size[1])
                except:
                    raise Usage("Screen resolution invalid")
            elif o in ['-c', '--config']:
                    readConfigFile(v, cfg)

        # Remaining arg is octoprint host
        if len(args) == 1:
            hostURI = args[0]
        else:
            hostURI = "http://{:s}:{:d}".format(cfg.host, cfg.port)

        if cfg.api_key is None:
            raise Usage("Octoprint API key required")

        try:
            logfmt = '%(asctime)s.%(msecs)03d  OctoPyClient%(levelname)8s %(filename)s:%(lineno)d - %(message)s'
            logtime = '%H:%M:%S'
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

            ui = UI(hostURI, cfg.api_key, width, height, style_sheet)

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
        eprint(err.msg)
        eprint("for help use --help")
        return 2

    finally:
        logging.shutdown()
        return
