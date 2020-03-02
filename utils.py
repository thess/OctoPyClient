# Utility functions for OctoPyClient

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def errToUser(err):
    text = err.args[0]['text']
    if "connection refused" in text:
        return "Unable to connect to Octoprint - is it running?"
    elif "request canceled" in text:
        return "Starting..."
    elif "connection broken" in text:
        return "Starting..."

    return "Unexpected error: {}".format(err)

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

def isFolder(file):
    if file['type'] == "folder":
        return True
    else: return False

def emptyContainer(list):
    ch = Gtk.Container.get_children(list)
    for widget in ch:
        list.remove(widget)

