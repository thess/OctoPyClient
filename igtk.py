# Misc wrapper functions for Gtk object manipulation

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from attr import dataclass

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

def ImageFromFileWithSize(img, w, h):
    p = Gdk.Pixbuf.new_from_file_at_scale(imagePath(img), w, h, True)
    i = Gtk.Image.new_from_pixbuf(p)
    return i

@dataclass
class imageLabel:
    l: Gtk.Label
    b: Gtk.Box

LABEL_IMAGE_SIZE = 60

# LabelWithImage returns a new imageLabel based on a gtk.Box containing
# a gtk.Label with a gtk.Image, the image is scaled at LABEL_IMAGE_SIZE.
def LabelWithImage(img, label, *args):
    l = FmtLabel(label, args)
    b = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    b.Add(ImageFromFileWithSize(img, LABEL_IMAGE_SIZE, LABEL_IMAGE_SIZE))
    b.Add(l)

    return imageLabel(l, b)


# ButtonImage returns a new gtk.Button with the given label, image and
# clicked callback.

def ButtonImageStyle(label, img, style, clicked):
    b = ButtonImage(label, img, clicked)

    ctx = b.get_style_context()
    ctx.add_class(style)

    return b


def ButtonImage(label, imgName, clicked):
    img = ImageFromFile(imgName)
    b = Gtk.Button(label=label)
    b.set_image(img)
    b.set_always_show_image(True)
    b.set_image_position(Gtk.PositionType.TOP)
    b.set_vexpand(True)
    b.set_hexpand(True)

    if clicked is not None:
        b.connect("clicked", clicked)

    return b
