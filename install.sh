#!/bin/bash

mkdir -p /usr/libexec/applets/
cp org.mate.*.service /usr/share/dbus-1/services/
cp org.mate.*.mate-panel-applet /usr/share/mate-panel/applets/
cp ./nvidia-gpu-temp.py /usr/libexec/applets/
