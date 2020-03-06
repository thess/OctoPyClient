# Misc wrapper functions for Gtk object manipulation
from attr import dataclass

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk, GdkPixbuf

def imagePath(iname):
    return "./styles/images/" + iname

def FmtLabel(string, *args):
    l = Gtk.Label()
    l.set_markup(string.format(args))
    return l

def ImageFromFile(imgname):
    img = Gtk.Image()
    img.set_from_file(imagePath(imgname))
    return img

def ImageFromFileWithSize(imgname, w, h):
    p = GdkPixbuf.Pixbuf.new_from_file_at_scale(imagePath(imgname), w, h, True)
    img = Gtk.Image.new_from_pixbuf(p)
    return img

@dataclass
class imageLabel:
    l: Gtk.Label
    b: Gtk.Box

LABEL_IMAGE_SIZE = 20

# LabelWithImage returns a new imageLabel based on a gtk.Box containing
# a gtk.Label with a gtk.Image, the image is scaled at LABEL_IMAGE_SIZE.
def LabelWithImage(img, label, *args):
    l = FmtLabel(label, args)
    b = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
    b.add(ImageFromFileWithSize(img, LABEL_IMAGE_SIZE, LABEL_IMAGE_SIZE))
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
    b = ButtonImageFromFile(label, imgName, clicked, parms)

    ctx = b.get_style_context()
    ctx.add_class(style)

    return b

# Return gtk.Button with image sized (h x w) as specified
def ButtonImageWithSize(imgName, h, w, clicked, parms=None):
    img = ImageFromFileWithSize(imgName, h, w)
    return ButtonImage(None, img, clicked, parms)

# Return gtk.Button with image expanded to fit
def ButtonImageFromFile(label, imgName, clicked, parms=None):
    img = ImageFromFile(imgName)
    b = ButtonImage(label, img, clicked, parms)
    b.set_vexpand(True)
    b.set_hexpand(True)
    return b
