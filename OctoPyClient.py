#!/usr/bin/env python3

""" OctoPyClient [opts] Octoprint-server

Hostname or IP of Octoprint (default: localhost:5000)

Command-line opts:

-h, --help      This text
-v, --verbose   Turn on debug output
-k, --key       Octoprint API key
-s, --style     Location of CSS style sheet (default: style.css)
-l, --layout    Screen resolution (default: 480x320)
-c, --config    Location of Octoprint configuration (default: $HOME/.octoprint/config.yaml)

"""

import sys
import traceback
import time
import getopt

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from octorest import OctoRest
from ui import UI


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    # Parse any command-line args
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hvk:s:r:c:", ["help", "verbose", "key=",
                                                                "style=", "resolution=", "config="])
        except getopt.error as msg:
            raise Usage(msg)

        # Gather command options
        debug_output = False
        api_key = None
        width = 480
        height = 320

        for o, v in opts:
            if o == '-v':
                debug_output = True
            if o in ["-h", "--help"]:
                print(__doc__)
                return
            if o in ['-k', '--key']:
                api_key = v

        # Remaining arg is octoprint host
        if len(args) != 1:
            raise Usage("Octoprint host name or IP required.")

        if api_key is None:
            raise Usage("Octoprint API key required")

        try:
            Gtk.init()
            settings = Gtk.Settings.get_default()
            settings.set_property("gtk_application_prefer_dark_theme", True)

            ui = UI(args[0], api_key, width, height)

            ui.show_all()

            Gtk.main()


        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            # Cleanup connection
            if exc_type == KeyboardInterrupt:
                return 0
            eprint("-->Caught network or other error:")
            traceback.print_exception(exc_type, exc_value, exc_tb)

    except Usage as err:
        # Cleanup connection
        eprint(err.msg)
        eprint("for help use --help")
        return 2

    finally:
        # Cleanup connection
        return


if __name__ == "__main__":
    sys.exit(main())
