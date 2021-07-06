#!/usr/bin/env python3
# -*- coding: utf8 -*-

#-------------------------------------------------------------------------------------
# Mp3 Class, which takes care of itializing the sound player system, playing, stopping aand calculating lengths of the different audios.
# It has being implemented by means of the linux command line and standard program "mpg321". It could be, however, 
# implemented by means of a python library such as PyAudio (which should be considered in case we need more complex
# sound system in the future, such as several channels or dolby surround 5.1. 
#
# However, more relevant that mp3 player itself is the sound server which is used. The standard linu sound server is 
# pulse audio, hated by many. It has not being too satisfactory for this system either so we should consider changing to 
# the more complex but technically more appealing "jack" sound server. "Jack" sound server supports dolby surround 
# and it even has a client library for python:
#        - https://pypi.org/project/JACK-Client/ 
#
# Jack tutorials: https://libremusicproduction.com/articles/demystifying-jack-%E2%80%93-beginners-guide-getting-started-jack
#                 https://wiki.archlinux.org/index.php/JACK_Audio_Connection_Kit
#                 https://github.com/jackaudio/jackaudio.github.com/wiki
#
# How to set up microphone and earphones with Jack: http://www.penguinproducer.com/Blog/2011/11/using-multiple-devices-with-jack/
#
# About having both pulseaudio and jack in the same system: http://jackaudio.org/faq/pulseaudio_and_jack.html 
#
# (TO-DO: learn 5.1 dolby surround concepts, understand the jack python client (or jack native linux program)
#         and make the 5.1 dolby surround configuration work in the Odroid. If Jack gets too complicated, check whether 
#          the 5.1 can be done by pulseaudio and leave it as the sound server.
#          Also, investigate about having both and both server's method of 5.1. Try everything first in a Virtual Machine
#-------------------------------------------------------------------------------------

# [START import_libraries]
import os
import subprocess
import time
from parameters import *
# [END import_libraries]

class Mp3player:
    """ mp3 sound player class"""

    def __init__(self, audios_path, output_device, input_device = '0'):
        """ initialization of the sound server. The sound server used is the standard linux sound server: pulseaudio."""    
        #Important to kill pulseaudio and start it afterward. Otherwise the chances of working bad are higher (not too reliable system in ubuntu 18... i should look for a python library)
        os.system('killall pulseaudio')
        #os.system('pulseaudio --start')
        os.system('pulseaudio -D')
        # this is needed as sometimes pulseaudio might not detect devices when starting. For now leave it commented
        os.system('pacmd unload-module module-udev-detect && pacmd load-module module-udev-detect')
        os.system('pactl -- set-sink-volume 0 ' + str(OUTPUT_VOLUME))
        os.system('pacmd set-default-sink ' +  str(output_device))
        if (input_device != '0'):
            os.system('pacmd set-default-source ' + str(input_device))
        self.abs_path = audios_path

    def play_audio(self, rel_path, volume = OUTPUT_VOLUME):
        """ initialization of the sound server. The sound server used is the standard linux sound server: pulseaudio."""   
        filename =  os.path.join(self.abs_path, rel_path)
        os.system('pactl -- set-sink-volume 0 ' + str(volume) + '%' )
        os.system('killall mpg321 > /dev/null 2>&1')    
        if (DEBUG==0):
            os.system('mpg321 ' + filename + '.mp3 > /dev/null 2>&1 &')
        else:
            os.system('mpg321 ' + filename + '.mp3 &')
        #os.system('mpg321 ' + filename + '.mp3')
        return 1    
    
    def stop(self):
        os.system('killall mpg321 > /dev/null 2>&1')
        return 1
    
    def audio_length(self, rel_path):
        filename = os.path.join(self.abs_path, rel_path)
        audio_length = subprocess.check_output('mp3info -p "%S" ' + filename + '.mp3', shell=True)
        return audio_length

        
    def play_audio_and_wait(self, rel_path):
        filename = os.path.join(self.abs_path, rel_path)
        length = self.audio_length(filename)
        self.play_audio(filename)
        time.sleep(int(length))
        return 1
