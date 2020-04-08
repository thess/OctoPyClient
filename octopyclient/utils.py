# Utility functions for OctoPyClient
import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Global logger defintion use: 'from utils import log'
# This allows us to have log levels independent of other libraries
# Logger and level initialized in main startup
import logging

log = logging.getLogger('OctoPyClient')

# Location of style sheet and images root
_stylesheet_base = os.path.realpath(os.path.dirname(__file__))

def setStyleBase(path):
    _stylesheet_base = path

def getStylePath(target):
    return os.path.join(_stylesheet_base, "styles", target)

def imagePath(iname):
    return os.path.join(_stylesheet_base, "styles/images", iname)

def errToUser(err):
    starting = ["Request canceled", "Connection aborted", "(404)"]
    text = str(err)
    if "Connection refused" in text:
        return "Unable to connect to OctoPrint - is it running?"
    elif "Name or service not known" in text:
        return "OctoPrint server not found - check address"
    elif "Forbidden" in text:
        return "OctoPrint login refused - check API key"
    elif any(ss in text for ss in starting):
        return "Service starting..."

    return "Unexpected error: {}".format(str(err))

def isRemoteDisconnect(err):
    if type(err).__name__ == 'ConnectionError':
        try:
            if type(err.args[0].args[1]).__name__ == 'RemoteDisconnected':
                return True
        except IndexError:
            # No subtype - must be other error
            pass
    return False

def strEllipsisLen(name, length):
    l = len(name)
    if l > length:
        return name[:int(length/3)] + "..." + name[l - int(length/3):l]

    return name

def strEllipsis(name):
    l = len(name)
    if l > 32:
        return name[:12] + "..." + name[l - 17:l]

    return name

def filenameEllipsis(name):
    idx = name.rfind(".gco")
    if idx > 0:
        name = name[:idx]

    if len(name) > 35:
        return name[:32] + "..."

    return name

def isFolder(file):
    if file['type'] == "folder":
        return True
    else: return False

def isOperational(state):
    return state in ["Operational", "Transfering"]

def isPrinting(state):
    return state in ["Printing", "Starting", "Pausing", "Paused", "Resuming", "Cancelling"]

def isOffline(state):
    return state in ["Offline", "Closed"]

def isError(state):
    return state in ["Error", "Unknown"]

def isConnecting(state):
    return state in ["Opening", "Detecting", "Connecting"]

def emptyContainer(list):
    ch = Gtk.Container.get_children(list)
    for widget in ch:
        list.remove(widget)

def confirmDialog(panel, msg, cb, param):
    dlg = Gtk.MessageDialog(parent=panel.ui.mainwin,
                            flags=Gtk.DialogFlags.MODAL,
                            type=Gtk.MessageType.QUESTION,
                            buttons=Gtk.ButtonsType.OK_CANCEL)
    dlg.set_decorated(False)
    dlg.set_markup(msg)

    box = dlg.get_content_area()
    box.set_margin_start(15)
    box.set_margin_end(15)
    box.set_margin_top(15)
    box.set_margin_bottom(15)

    ctx = dlg.get_style_context()
    ctx.add_class("dialog")
    try:
        if dlg.run() == Gtk.ResponseType.OK:
            cb(panel, param)
    finally:
        dlg.destroy()

def fixupHTML(msg):
    # replace 'strong' with 'b'
    msg = msg.replace("<strong>", "<b>")
    msg = msg.replace("</strong>", "</b>")
    # remove 'p'
    msg = msg.replace("<p>", " ")
    msg = msg.replace("</p>", " ")

    return msg
