#!/bin/bash

# Check whether there is internet connection or not by checking connection to google.

wget -q --spider http://google.com

# "$?" is a special bash variable which gets the value of the last command exit status.
if [ $? -eq 0 ]; then
    echo "Online" > network-status-service-up.txt
else
    echo "Offline" > network-status-service-up.txt
fi
