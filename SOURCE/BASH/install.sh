#!/bin/bash


# ------------------- TO DO ------------------------------------------------------
#-- Remember to change the ownership of the /dev/i2c-1 and the /dev/gpiomem files and creating the group gpio and making the file 
#   gpiomem and i2c-1 owned by root and the group gpio and i2c (respectively) and adding odroid user to both grpups
#   and then doing the chmod 666 /dev/i2c-1 (y con gpiomem).  (TO DO)

## - Create the service file for starting in unit (see steps. add service file and user and group things)

##- Remember to make Odroid not need password for sudo adding in a sudoers.d/ file "Odroid ALL=(ALL) NOPASSWD: ALL" and saving it 
##  and setting its sudo chmod 0440 "file"

## Add options to be able to install everything without upgrading (TO DO)
# ------------------- TO DO ------------------------------------------------------

# updating and upgrading the system
sudo apt-get update
sudo apt-get upgrade

# checking whether python3 is installed and installing it if not.
command -v python3 >/dev/null 2>&1 || sudo apt-get install -y python3

# checking whether pip3 is installed and installing it if not.
command -v pip3 >/dev/null 2>&1 || sudo apt-get install -y python3-pip

# installing i2c dependencies.
command -v python-smbus >/dev/null 2>&1 || sudo apt-get install -y python-smbus
command -v i2c-tools >/dev/null 2>&1 || sudo apt-get install -y i2c-tools

# installing MPG321 for playing audio and the mp3info program for knowing audios length
command -v mpg321 >/dev/null 2>&1 || sudo apt-get install mpg321
command -v mp3info >/dev/null 2>&1 || sudo apt-get install mp3info

# installing Adafruit_GPIO for python3
pip3 install --user Adafruit_GPIO

# installation of Google Speech API 
pip3 install --upgrade google-cloud-storage and pip3 install google-cloud-speech

# installing pyaudio
pip3 install --user pyaudio

#install the wiringPi python wrapper for Odroid
sudo apt-get install git python-dev python-setuptools python3-dev python3-setuptools swig
git clone --recursive https://github.com/hardkernel/WiringPi2-Python
cd WiringPi2-Python
python3 setup.py install





  
