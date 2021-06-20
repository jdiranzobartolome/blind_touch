#!/usr/bin/env python3
# -*- coding: utf8 -*-

#-------------------------------------------------------------------------------------
# All parameters which the user might want to change for the system are defined here.
# They are all defined in capital letters, which represents that they 
# are constant parameters during execution time and help differentiate them while reading the code. 

# Author: Jorge David Iranzo
#-------------------------------------------------------------------------------------
# [START Set_Prameters]

# variables which define the amount of console output from the program. DEBUG variable defines general information which can help debugging the system.
# VOICE_FEEDBACK is used for activating of deactivating the real-time feedback related to the words google voice API is listening to. It can also be
# useful for debugging. Similarly, TAPPING_FEEDBACK is used to activate feedback related to the tapping recognition. 

import os

DEBUG = 1
TAPPING_FEEDBACK = 1
VOICE_FEEDBACK = 1
CONTROL_API = 1

# Menu setable Default values
DEFAULT_PAINT = 2                    # 0: starry night, 1: cezanne's still life, 2: Bird
DEFAULT_INITIAL_AUDIO_MODE = 0       # 0: no audio, 1: instructions and general info about the painting (long), 2: only instructions
DEFAULT_EFFECT_MODE = 0              # 0: off, 1: on
DEFAULT_LANGUAGE = 'en-US'           # 'ko-KR': Korean, 'en-US': English, 'es-ES': Spanish

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# WiringPi Interrput Pin
INTERRUPT_PIN = 7 # GPIO 7 in wiringPI library but pin 7(GPIO#18) in Shifter Shield

# UART parameters
SERIAL_DEV = "/dev/ttySAC0"  #Odroid shifter shield pins 10 (Rx) and 8 (Tx) and 12 (CTS)
BAUDS = 115200 

# Name of the input and output devices
# For finding out the name of your device, plug it in and do: 

#     for input device: $ pacmd list-sources | grep -e 'index:' -e device.string -e 'name:'
#     for output device: $ pacmd "set-default-source alsa_output.pci-0000_04_01.0.analog-stereo.monitor"

# A list with all the input and output devices and their string name will appear. 
#
# If the microphone is listed when doing "$ lsusb" and "arecord -l", but not in the output devices of pulse audio run the bash script "recognizing_mic.sh". (TO DO)
#input and output device for old microphone and the sound card with earphones:
#INPUT_DEVICE = "alsa_input.usb-0c76_USB_Audio_Device-00.analog-mono"
#OUTPUT_DEVICE = "alsa_output.usb-C-Media_Electronics_Inc._USB_PnP_Sound_Device-00.analog-stereo"
#input and output device for our Logitech Headset
INPUT_DEVICE = "alsa_input.usb-Logitech_Logitech_USB_Headset-00.analog-mono"
OUTPUT_DEVICE= "alsa_output.usb-Logitech_Logitech_USB_Headset-00.analog-stereo"
# Output device volume level (50 ==> 50% of level. Max is 100, min is 0)
OUTPUT_VOLUME = 50

## kwake-up-words from the different languages (diccionario {'BCP-47 language tag': 'keyword1|keyword2|keyword3...'}. 
# Do not modify as it affects other code not optimized for modification yet. 
KEY_WORD_KR = "inicio|설명|final"
KEY_WORD_EN = "explanation"
KEY_WORD_SP = "explicación"
KEY_WORD = { "ko-KR": KEY_WORD_KR, "en-US": KEY_WORD_EN, "es-ES": KEY_WORD_SP}

## command for stopping audio when listening to it in different languages (diccionario {'BCP-47 language tag': 'keyword1|keyword2|keyword3...'}
# Do not modify as it affects other code not optimized for modification yet.
KEY_STOP_KR = "inicio|정지|끝|final"
KEY_STOP_EN = "stop|finish"
KEY_STOP_SP = "para"
KEY_STOP = { "ko-KR": KEY_STOP_KR, "en-US": KEY_STOP_EN, "es-ES": KEY_STOP_SP}

## keywords from the different languages (diccionario {'BCP-47 language tag': 'keyword1|keyword2|keyword3...'}
# Do not modify as it affects other code not optimized for modification yet.
KEY_PHRASES_KR = "inicio|그림|화가|사용 방법|사용방법|옵션|끝|음악|사운드|final"
KEY_PHRASES_EN = "painting|painter|music|options|instructions|finish"
KEY_PHRASES_SP = "pintura|pìntor|ayuda"
KEY_PHRASES = { "ko-KR": KEY_PHRASES_KR, "en-US": KEY_PHRASES_EN, "es-ES": KEY_PHRASES_SP}

# Google API-KEY json path environment. Only one of next two lines have to be  uncommented
# Uncomment next line for writing the absolute path by yourself
# APIKEY_PATH = "/home/odroid/art_project_global/art_project_global/dual_bird_MPR121/odroid/api-key.json"
# Uncomment next line for using relative path (read README_PROJECT_FOLDER file for info on how the folder tree needs to be arranged)
APIKEY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "api-key.json"))

# Path of the main audio folder root. Check the read me file for knowing how to folders need to be arranged. As a reminder, an example of an 
# audio folder might be:
# (TO DO)
# Uncomment next line for writing the absolute path by yourself
# AUDIOS_PATH = "/home/odroid/art_project_global/art_project_global/"
# Uncomment next line for using relative path (read README_PROJECT_FOLDER file for info on how the folder tree needs to be arranged)
AUDIOS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))

# MPR121 parameters. Defines the intervals which are consider acceptable for a fast and slow tapping,
# and the threshold of the touch sensor. 
SLOWEST_TAPPING_INTERVAL = 0.4
FASTEST_TAPPING_INTERVAL = 0.1
MPR121_TOUCH_THRESHOLD = 40
MPR121_RELEASE_THRESHOLD = 20

# [END Set_Parameters]
