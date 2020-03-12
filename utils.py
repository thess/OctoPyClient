# Utility functions for OctoPyClient

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Global logger defintion use: 'from utils import log'
# This allows us to have log levels independent of other libraries
# Logger and level initialized in main startup
import logging

log = logging.getLogger('OctoPyClient')

def errToUser(err):
    text = str(err)
    if "Connection refused" in text:
        return "Unable to connect to OctoPrint - is it running?"
    elif "Name or service not known" in text:
        return "OctoPrint server not found - check address"
    elif "Forbidden" in text:
        return "OctoPrint login refused - check API key"
    elif "Connection aborted" in text:
        return "Starting..."
    elif "Request canceled" in text:
        return "Starting..."

    return "Unexpected error: {}".format(str(err))

def isRemoteDisconnect(err):
    if (type(err).__name__ == 'ConnectionError') \
            and (type(err.args[0].args[1]).__name__ == 'RemoteDisconnected'):
        return True
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
    dlg = Gtk.MessageDialog(parent=panel.ui.win,
                            flags=Gtk.DialogFlags.MODAL,
                            type=Gtk.MessageType.QUESTION,
                            buttons=Gtk.ButtonsType.OK_CANCEL)
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
