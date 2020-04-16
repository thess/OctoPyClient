#!/bin/sh

# Example script to disable screen blanking. Screen number may be given.
# Ex: $ ./dpms.sh 1
# Preferred use: Supply '--noblank' option to octopyclient command-line.

dpy=${1:-0}

export DISPLAY=:${dpy}
xset s off         # don't activate screensaver
xset -dpms         # disable DPMS (Energy Star) features.
xset s noblank     # don't blank the video device
