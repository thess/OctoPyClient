import logging
import threading
from common import CommonPanel, Singleton, BackgroundTask

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import igtk

class PrintStatusPanel(CommonPanel, metaclass=Singleton):
    pb: Gtk.ProgressBar

    def __init__(self, ui, parent):
        CommonPanel.__init__(self, ui, parent)
        logging.debug("PrintStatusPanel created")
        self.bkgnd = BackgroundTask(ui, "print_status", 1, self.update)

        self.g.attach(self.createMainBox(), 1, 0, 4, 2)
        self.arrangeButtons(False)

        self.taskRunning = threading.Lock()
        self.printerStatus = 0

    def createProgressBar(self):
        self.pb = Gtk.ProgressBar()
        self.pb.set_show_text(True)
        self.pb.set_name("PrintProg")
        return self.pb

    def createMainBox(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_valign(Gtk.Align.START)
        box.set_vexpand(True)

        grid = Gtk.Grid()
        grid.set_hexpand(True)
        grid.add(self.createInfoBox())
        grid.set_valign(Gtk.Align.START)
        grid.set_margin_top(20)

        box.add(grid)

        pb_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        pb_box.set_vexpand(True)
        pb_box.set_hexpand(True)
        pb_box.add(self.createProgressBar())

        box.add(pb_box)

        btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        btn.set_halign(Gtk.Align.END)
        btn.set_valign(Gtk.Align.END)
        btn.set_vexpand(True)
        btn.set_margin_top(0)
        btn.set_margin_end(0)
        btn.add(self.createPrintButton())
        btn.add(self.createPauseButton())
        btn.add(self.createStopButton())
        btn.add(igtk.ButtonImageWithSize("back.svg", self.Scaled(60), self.Scaled(60), self.ui.navHistory))

        box.add(btn)
        return box

    def createInfoBox(self):
        self.file = igtk.LabelWithImage("file2.svg", "")
        self.left = igtk.LabelWithImage("speed-step2.svg", "")
        self.finish = igtk.LabelWithImage("finish.svg", "")
        self.bed = igtk.LabelWithImage("bed2.svg", "")
        self.tool0 = igtk.LabelWithImage("extruder2.svg", "")

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info.set_halign(Gtk.Align.START)
        info.set_hexpand(True)
        info.set_margin_start(20)

        info.add(self.file.b)
        info.add(self.left.b)
        info.add(self.finish.b)
        info.add(self.tool0.b)
        info.add(self.bed.b)

        return info

    def createPrintButton(self):
        self.print = igtk.ButtonImageWithSize("print2.svg", self.Scaled(60), self.Scaled(60), self.doPrint)
        return self.print

    def createPauseButton(self):
        self.pause = igtk.ButtonImageWithSize("pause2.svg", self.Scaled(60), self.Scaled(60), self.doPause)
        return self.pause

    def createStopButton(self):
        self.stop = igtk.ButtonImageWithSize("stop2.svg", self.Scaled(60), self.Scaled(60), self.doStop)
        return self.stop

    def doPrint(self, source):
        pass

    def doStop(self, source):
        pass

    def doPause(self):
        pass

    def update(self):
        if self.bkgnd.lock.acquire(False):
            try:
                self.updateTemperature()
                self.updateJob()
            finally:
                self.bkgnd.lock.release()

    def updateTemperature(self):
        # Fake printing info
        self.print.set_sensitive(False)
        text ="{:.0f}°C ⇒ {:.0f}°C ".format(45, 60)
        self.bed.l.set_label(text)
        text ="{:.0f}°C ⇒ {:.0f}°C ".format(170, 230)
        self.tool0.l.set_label(text)

    def updateJob(self):
        self.file.l.set_label("<i>File not set</i>")

        self.pb.set_fraction(0.50)

        self.left.l.set_label("Elapsed: 69 minutes")
        self.finish.l.set_label("Any moment now")
