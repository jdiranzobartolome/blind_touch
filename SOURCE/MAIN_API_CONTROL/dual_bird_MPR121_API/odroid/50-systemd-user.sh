#!/bin/sh

file="/home/odroid/50-systemd-user--script-check.txt"

if [ -f $file ] ; then
    rm $file
fi

systemctl --user import-environment DISPLAY XAUTHORITY

if which dbus-update-activation-environment >/dev/null 2>&1; then
        dbus-update-activation-environment DISPLAY XAUTHORITY
fi

echo "50-systemd-user.sh script completed" > $file
