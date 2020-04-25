# Misc wrapper functions for Gtk object manipulation

from attr import dataclass
from typing import Callable

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib

gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf

from .utils import *

def FmtLabel(string, *args):
    l = Gtk.Label()
    l.set_markup(string.format(args))
    return l

def ImageFromFile(imgname):
    try:
        p = GdkPixbuf.Pixbuf.new_from_file(imagePath(imgname))
        img = Gtk.Image.new_from_pixbuf(p)
    except:
        return Gtk.Image.new_from_stock(Gtk.STOCK_MISSING_IMAGE, Gtk.IconSize.BUTTON)
    return img

def ImageFromFileScaled(imgname):
    try:
        p = GdkPixbuf.Pixbuf.new_from_file(imagePath(imgname))
        w = displayScale(p.get_width())
        h = displayScale(p.get_height())
        ps = p.scale_simple(w, h, GdkPixbuf.InterpType.BILINEAR)
        img = Gtk.Image.new_from_pixbuf(ps)
    except Exception as err:
        return Gtk.Image.new_from_stock(Gtk.STOCK_MISSING_IMAGE, Gtk.IconSize.BUTTON)
    return img

def ImageFromFileWithSize2(imgname, w, h):
    try:
        p = GdkPixbuf.Pixbuf.new_from_file_at_scale(imagePath(imgname), w, h, True)
        img = Gtk.Image.new_from_pixbuf(p)
    except:
        return Gtk.Image.new_from_stock(Gtk.STOCK_MISSING_IMAGE, Gtk.IconSize.BUTTON)
    return img

def ImageFromFileWithSize(imgname, size):
    return ImageFromFileWithSize2(imgname, size, size)

@dataclass
class imageLabel:
    l: Gtk.Label
    b: Gtk.Box

# LabelWithImage returns a new imageLabel based on a gtk.Box containing
# a gtk.Label with a gtk.Image, the image is scaled at LABEL_IMAGE_SIZE.
def LabelWithImage(img, imgSize, label, *args):
    l = FmtLabel(label, args)
    b = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
    b.add(ImageFromFileWithSize(img, displayScale(imgSize)))
    b.add(l)

    return imageLabel(l, b)

# ButtonImage returns a new gtk.Button with the given label, image and
# clicked callback.

def ButtonImage(label, img, clicked, parms=None):
    b = Gtk.Button(label=label)
    b.set_image(img)
    b.set_always_show_image(True)
    b.set_image_position(Gtk.PositionType.TOP)

    if clicked is not None:
        if parms is None:
            b.connect("clicked", clicked)
        else:
            b.connect("clicked", clicked, parms)
    return b

# Return gtk.Button with image and applied style
def ButtonImageStyle(label, imgName, style, clicked, parms=None):
    b = ButtonImageScaled(label, imgName, IMAGE_SIZE_NORMAL, clicked, parms)
    ctx = b.get_style_context()
    ctx.add_class(style)
    return b

# Return gtk.Button with image sized as specified
def ButtonImageWithSize(imgName, imgSize, clicked, parms=None):
    img = ImageFromFileWithSize(imgName, imgSize)
    return ButtonImage(None, img, clicked, parms)

# Return gtk.Button with image scaled and expanded to fit
def ButtonImageScaled(label, imgName, imgSize, clicked, parms=None):
    scaledSize = displayScale(imgSize)
    img = ImageFromFileWithSize(imgName, scaledSize)
    b = ButtonImage(label, img, clicked, parms)
    b.set_vexpand(True)
    b.set_hexpand(True)
    return b

@dataclass
class StepButton:
    idx:   int          # current value
    steps:  []          # possible (label, value) tuples
    stcb:   Callable[..., None] # button update callback
    b:      Gtk.Button  # associated button

def createStepButton(image, steps, callback=None):
    lbl = ""
    if len(steps) > 0:
        lbl = steps[0][0]

    sb = StepButton(idx = 0, steps=steps, stcb=callback, b=None)
    # Fill in struct with button reference
    sb.b = ButtonImageScaled(lbl, image, IMAGE_SIZE_NORMAL, advStep, sb)

    return sb

def advStep(btn, sb):
    sb.idx += 1
    if sb.idx >= len(sb.steps):
        sb.idx = 0

    btn.set_label(sb.steps[sb.idx][0])
    if sb.stcb is not None:
        sb.stcb()

def addStep(sb, step):
    if len(sb.steps) == 0:
        sb.b.set_label(step[0])
    sb.steps.append(step)

@dataclass
class PressedButton:
    released:   bool        # button released flag
    b:          Gtk.Button  # associated button
    pcb:        Callable[..., None] # pressed interval callback
    cbint:      int         # callback interval (ms)

def createPressedButton(label, image, ms, pressed, param=None):
    btn = ButtonImageScaled(label, image, IMAGE_SIZE_NORMAL, None)
    pb = PressedButton(False, btn, pressed, ms)

    if pressed is not None:
        btn.connect("pressed", doButtonPressed, pb, param)

    btn.connect("released", doButtonReleased, pb)
    return pb

def doButtonPressed(btn, pb, param):
    pb.released = False
    # Callback immediately before 1st interval
    if not pb.pcb(pb, param):
        return

    # Queue timer next to idle dispatch
    GLib.timeout_add(pb.cbint, pb.pcb, pb, param)

def doButtonReleased(btn, pb):
    # Signal timer to exit
    pb.released = True
