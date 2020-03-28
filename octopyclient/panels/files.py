# Show local files, navigate folders.
# Options to delete files/folders and start print jobs

import time
import humanize

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from octopyclient.common import CommonPanel, Singleton
from octopyclient.igtk import *
from octopyclient.utils import *

@dataclass
class locationHistory:
    locations: [str]

def currentLoc(lh):
    return lh.locations[len(lh.locations) - 1]

def goDown(lh, folder):
    newLocation = currentLoc(lh) + "/" + folder
    lh.locations.append(newLocation)

def goUp(lh):
    lh.locations.pop()

def isRoot(lh):
    if len(lh.locations) > 1:
        return False
    else: return True

def byDate(item):
    if item['type'] == "folder":
        key = 0
    else:
        key = item['date']
    return key

class FilesPanel(CommonPanel, metaclass=Singleton):
    def __init__(self, ui):
        CommonPanel.__init__(self, ui)
        log.debug("FilesPanel created")

        self.location = locationHistory(['local'])
        self.list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.list.set_vexpand(True)

        sw = Gtk.ScrolledWindow()
        sw.add(self.list)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.add(sw)
        box.add(self.createActionBar())
        self.g.add(box)

        self.doLoadFiles()

    def createActionBar(self):
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        bar.set_halign(Gtk.Align.END)
        bar.set_hexpand(True)
        bar.set_margin_top(5)
        bar.set_margin_bottom(5)
        bar.set_margin_end(5)

        bar.add(self.createRefreshButton())
        bar.add(self.createBackButton())

        return bar

    def createRefreshButton(self):
        return ButtonImageWithSize("refresh.svg", self.Scaled(35), self.Scaled(35), self.doLoadFiles)

    def createBackButton(self):
        return ButtonImageWithSize("back.svg", self.Scaled(35), self.Scaled(35), self.filesNavigate)

    def filesNavigate(self, source):
        if isRoot(self.location):
            self.ui.navigateBack(source)
        else:
            goUp(self.location)
            self.doLoadFiles()

    def doLoadFiles(self, source=None):
        log.info("Loading list of files from: {}".format(currentLoc(self.location)))
        files = []
        try:
            folder = self.ui.printer.files(location=currentLoc(self.location), recursive=False)
            if 'files' in folder:
                files = folder['files']
            elif 'children' in folder:
                if len(folder['children']) > 0:
                    files = folder['children']
        except Exception as err:
            log.error("Retrieving files: {}".format(str(err)))
            return

        # Sort latest first
        files.sort(key=byDate, reverse=True)
        # Remove previous list items from container
        emptyContainer(self.list)
        # Folders first
        for f in files:
            if isFolder(f):
                self.addFolder(self.list, f)

        for f in files:
            if not isFolder(f):
                self.addFile(self.list, f)

        self.list.show_all()

    def addFolder(self, list, f):
        frame = Gtk.Frame()

        name = Gtk.Label(f['name'])
        name.set_markup("<big>{:s}</big>".format(strEllipsis(f['name'])))
        name.set_hexpand(True)
        name.set_halign(Gtk.Align.START)
        name.set_margin_top(15)
        name.set_margin_start(10)

        # info = Gtk.Label()
        # info.set_halign(Gtk.Align.START)
        # info.set_markup("<small>Size: <b>{:s}</b></small>".format(humanize.naturalsize(f['size'])))

        labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        labels.add(name)
        # labels.add(info)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        actions.add(self.createDeleteButton("delete.svg", f))
        actions.add(self.createOpenFolderButton(f))

        file = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        file.set_margin_top(5)
        file.set_margin_bottom(5)
        file.set_margin_start(15)
        file.set_margin_end(15)
        file.set_hexpand(True)

        file.add(ImageFromFileWithSize("folder.svg", self.Scaled(35), self.Scaled(35)))
        file.add(labels)
        file.add(actions)

        frame.add(file)
        list.add(frame)

    def addFile(self, list, f):
        frame = Gtk.Frame()

        name = Gtk.Label(f['name'])
        name.set_markup("<small>{:s}</small>".format(strEllipsis(f['name'])))
        name.set_hexpand(True)
        name.set_halign(Gtk.Align.START)
        name.set_margin_top(5)

        info = Gtk.Label()
        info.set_halign(Gtk.Align.START)
        info.set_markup("<small>Uploaded: <b>{:s}</b> - Size: <b>{:s}</b></small>"
                        .format(humanize.naturaltime(time.time() - f['date']), humanize.naturalsize(f['size'])))
        labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        labels.add(name)
        labels.add(info)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        actions.add(self.createDeleteButton("delete.svg", f))
        actions.add(self.createPrintButton("print2.svg", f))
        actions.set_halign(Gtk.Align.END)

        file = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        file.set_margin_top(5)
        file.set_margin_bottom(5)
        file.set_margin_start(5)
        file.set_margin_end(15)
        file.set_hexpand(True)

        file.add(ImageFromFileWithSize("file.svg", self.Scaled(35), self.Scaled(35)))
        file.add(labels)
        file.add(actions)

        frame.add(file)
        list.add(frame)

    def createOpenFolderButton(self, folder):
        b = ButtonImageWithSize("open.svg", self.Scaled(35), self.Scaled(35), self.openFolder, folder)

        ctx = b.get_style_context()
        # ctx.add_class("color1")
        ctx.add_class("file-list")

        return b

    def createPrintButton(self, img, file):
        b = ButtonImageWithSize(img, self.Scaled(35), self.Scaled(35), self.askPrintFile, file)

        ctx = b.get_style_context()
        # ctx.add_class("color3")
        ctx.add_class("file-list")

        return b

    def createDeleteButton(self, img, file):
        b = ButtonImageWithSize(img, self.Scaled(35), self.Scaled(35), self.askDeleteFile, file)

        ctx = b.get_style_context()
        # ctx.add_class("color2")
        ctx.add_class("file-list")

        return b

    def openFolder(self, source, file):
        goDown(self.location, file['path'])
        self.doLoadFiles()

    def askPrintFile(self, source, file):
        confirmDialog(self, "Send file to printer?\n\n<b>{:s}</b>"
                      .format(strEllipsisLen(file['name'], 27)), doPrintFile, file)

    def askDeleteFile(self, source, file):
        msg = "Delete file?" if not isFolder(file) else "Remove folder and its contents?"
        confirmDialog(self, "{:s}\n\n<b>{:s}</b>"
                      .format(msg, strEllipsisLen(file['name'], 27)), doDeleteFile, file)

def doPrintFile(panel, file):
    try:
        log.info("Load and Print file: {:s}".format(file['path']))
        panel.ui.printer.select(file['path'], print=True)
    except Exception as err:
        log.error("Print start request: {}".format(str(err)))


def doDeleteFile(panel, file):
    try:
        log.info("RM {:s} FROM {:s}".format(file['path'], "local"))
        panel.ui.printer.delete(file['path'])
    except Exception as err:
        log.error("Delete object: {}".format(str(err)))
    finally:
        # Re-display files list
        panel.doLoadFiles()
