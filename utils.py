# Utility functions for OctoPyClient

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def errToUser(err):
    text = str(err)
    if "connection refused" in text:
        return "Unable to connect to Octoprint - is it running?"
    elif "request canceled" in text:
        return "Starting..."
    elif "connection broken" in text:
        return "Starting..."

    return "Unexpected error: {}".format(str(err))

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
    if len(name) > 35:
        return name[:32] + "..."

    return name

def isFolder(file):
    if file['type'] == "folder":
        return True
    else: return False

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
