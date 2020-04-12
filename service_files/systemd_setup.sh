#!/bin/bash

# Must be root
if [[ $EUID -ne 0 ]]; then
        echo Not running as root
        exit 1
fi

# Make sure install dir exists
mkdir -p /usr/local/bin

cd service_files
cp -a dpy /usr/local/bin
cp -a octopyclient.env /etc
cp -a octopyclient.service /etc/systemd/system

systemctl daemon-reload

# Enabling octopyclient.service will set it for graphical-target startup
# and as the display-manager service.
#   $ systemctl enable octopyclient
#   $ systemctl set-default graphical.target
#   $ systemctl start octopyclient
