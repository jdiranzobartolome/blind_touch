#!/usr/bin/env python3
# -*- coding: utf8 -*-

#-------------------------------------------------------------------------------------
# Main thread of the tapping mode (touch recognition thread). Due to the need to be constantly listening to the wake-up-word
# even during tapping mode, there is the need of running both threads (voice thread and tapping thread) in parallel
# for most of the system usage time. A threadLock is used in order to execute only one of the threads when needed (for
# example, the tapping thread will not run when the user enters the VUI and the microphone thread will not run when the user 
# is listening to an on-going audio in tapping mode).  

# Author: Jorge David Iranzo
#-------------------------------------------------------------------------------------

import threading
import time
from MPR121 import MPR121
from Mp3player import Mp3player
from parameters import *

exitFlag = 0

class TappingThread (threading.Thread):
   """Representation of the touch recognition functioning thread"""

   def __init__(self, name, threadLock,  cap, mp3player, paint_mode, language_code):
      """Create an instance of the thread."""
      threading.Thread.__init__(self)
      self.name = name
      self.threadLock = threadLock
      self.mp3player = mp3player
      self.MPR121 = cap
      self.paint_mode = paint_mode
      self.language_code = language_code
   def run(self):
      """Starts execution of the thread"""
      print ("Starting " + str(self.name))
      tapping_thread_main(self.threadLock, self.MPR121, self.mp3player, self.paint_mode, self.language_code)
      print ("Exiting " + str(self.name))


def tapping_thread_main(threadLock, MPR121, mp3player, paint_mode, language_code):
    """ Execution function of the thread. It basically consists on different iterating through two steps which read the tapping events.
    In one of the steps the audio is started an in the other (when tapping_mode_bool = False, the audio is stopped if tapping event 
    takes place. """

    # When False, the tapping thread will not play audio according to double or triple tapping but it will just stop audio when tapping. 
    # Besides, the voice thread will not work. This variable is False anytime the user is listening to an audio after a tapping event.
    tapping_mode_bool = True
    
    while True:
            
        if (tapping_mode_bool == False):
        ## set a timeout for the read function of "audio length" and it returns "None" if tomeout reached. We can know whether the audio finished this way. 
            zone, numtap = MPR121.is_tapping_one_finger_zone(length)
        else:
        ## no time out, so the MPR121 will wait for a tapping event forever. 
            zone, numtap = MPR121.is_tapping_one_finger_zone()

        if ((threadLock.locked() == False) or (tapping_mode_bool == False)):        
            # Get lock to synchronize threads. From now on, till the lock gets free, only this thread will execute
            if (tapping_mode_bool != False):
                threadLock.acquire()
                if (DEBUG == 1):
                    print("threadLock acquired by tapping thread")
   
            if (TAPPING_FEEDBACK == 1):
                print('zoned tapped = ' + str(zone))
                print('numbero f taps = ' + str(numtap))
    
            if ((tapping_mode_bool) and (numtap == 2 )):
                tapping_mode_bool = False
                rel_path = str(language_code) + '/' + str(paint_mode) + '/explanation/' + str(zone)
                if (DEBUG == 1):
                    print('playing audio after double tapping')
                length = mp3player.audio_length(rel_path)
                mp3player.play_audio(rel_path)      
                
            elif ((tapping_mode_bool) and (numtap == 3)):
                tapping_mode_bool = False
                rel_path = str(language_code) + '/' + str(paint_mode) + '/sound/' + str(zone)
                if (DEBUG == 1):
                    print('playing audio after triple tapping')
                length = mp3player.audio_length(rel_path)
                mp3player.play_audio(rel_path) 
                
            elif ((tapping_mode_bool == False) and ((numtap == 2 ) or (numtap == 3))):
                if (DEBUG == 1):
                    print("stopping audio from tapping mode")
                tapping_mode_bool = True
                # Free lock to release other thread
                threadLock.release()
                mp3player.stop()
                if (DEBUG == 1):
                   print("threadLocke released by tapping thread") 
                
            elif ((tapping_mode_bool == False) and (zone is None) and (numtap is None)):
                tapping_mode_bool = True
                # Free lock to release other thread
                threadLock.release()
                mp3player.stop()
                if (DEBUG == 1):
                   print("threadLocke released by tapping thread")
