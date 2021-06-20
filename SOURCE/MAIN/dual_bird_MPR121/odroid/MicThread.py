#!/usr/bin/env python3
# -*- coding: utf8 -*-

#-------------------------------------------------------------------------------------
# Main thread of the voice mode (voice recognition thread). Due to the need to be constantly listening to the wake-up-word
# even during tapping mode, there is the need of running both threads (voice thread and tapping thread) in parallel
# for most of the system usage time. A threadLock is used in order to execute only one of the threads when needed (for
# example, the tapping thread will not run when the user enters the VUI and the microphone thread will not run when the user 
# is listening to an on-going audio in tapping mode).  

# Author: Jorge David Iranzo
#-------------------------------------------------------------------------------------

import threading
import time
from Mp3player import Mp3player
from GoogleVoice import GoogleVoice
from parameters import *                 #in the end because of the debug variables I need to import parameters everywhere. I dont like

exitFlag = 0

class MicThread (threading.Thread):
   """Representation of the microphone functioning thread"""

   def __init__(self, name, threadLock,  mp3player, google_voice, paint_mode, language_code):
      """Create an instance of the thread."""
      threading.Thread.__init__(self)
      self.name = name
      self.threadLock = threadLock
      self.mp3player = mp3player
      self.google_voice = google_voice
      self.paint_mode = paint_mode
      self.language_code = language_code
   def run(self):
      """Starts execution of the thread"""
      print ("Starting " + str(self.name))
      mic_thread_main(self.threadLock, self.mp3player, self.google_voice, self.paint_mode, self.language_code)
      print ("Exiting " + str(self.name))


def listen_command_while_audio(mp3player, google_voice, language_code, length, keyword_bool):
    """ Function for listening to a command word while listening to an audio file. The variable length, which indicates the audio length,
    is used for knowing for how long the micrphone need to be aware of the words "stop" and "end", which can be used while listening to
    an audio file. 
        
    Returns True if the user said the keyword "end" (which indicates he/she wants to get out of the VUI. It returns False if the user
    says the command word "stop" or the audio file finishes (both events initialize the command selection prompt and menu of the VUI."""
    sentence = None
    audio_init = time.time()
    while ((sentence != u"끝") and (sentence != u"정지") and (sentence != u"stop") and (sentence != u"finish") and ((time.time() - audio_init) < length - 2)):
        #print(time.time())
        #print(length)
        #print(time.time() - audio_init)
        #print('---------------------------------------')
        length_left = int(length) - (time.time() - audio_init)
        sentence = google_voice.listen_command(keyword_bool,length_left)
        if (VOICE_FEEDBACK == 1):
            print("Google Speech Recognition thinks you said " + sentence + '.')
        time.sleep(1.5)
    if ((sentence == u"끝") or (sentence == "finish")):
        rel_path = str(language_code) + '/vui_dialog/final_words'
        mp3player.play_audio_and_wait(rel_path)
        return True
        
    elif ((sentence == u"정지") or (sentence == "stop")):
        rel_path = str(language_code) + '/vui_dialog/audio_finished'
        mp3player.play_audio(rel_path)
        return False
        
    else:
        return False
        
#
def mic_thread_main(threadLock, mp3player, google_voice, paint_mode, language_code):
   """ Execution function of the thread. It basically consists on different steps in which the threadLock is released or acquired and on
   calls to the Google API voice recognition function for the different keywords which apply at that time. """  
   ## boolean which indicates whether we are only listening for the keyword (which activates the voice user interface) or for the general commands
   ## which can be listened to once the dialog is going on). So when it is true, the listen_command() function only listens to the keyword.
   ## When it is false, the commands listened to by the mic are different depending on the variable "length" (zero, or different to zero). 
   keyword_bool = True
   
   while True:
        
        sentence = google_voice.listen_command(keyword_bool)
        if (VOICE_FEEDBACK == 1):
            print("Google Speech Recognition thinks you said " + sentence + '.')
             
        if (((sentence == u"설명") or (sentence == "explanation")) and (threadLock.locked() == False)):
            # Get lock to synchronize threads, from now on, till the lock gets free, only this thread will execute
            threadLock.acquire()
            if (DEBUG == 1):
                   print("threadLock acquired by voice thread")
            rel_path = str(language_code) + '/vui_dialog/initial_words'
            mp3player.play_audio(rel_path)
            keyword_bool = False

        # TO DO: make this cleaner by not hard-coding the words in the ifs, but rather using dictionaries or sth from parameters.
        # TO DO: Get rid of the "keyword_bool" variable. By using the listen_command_while_audio function yoo already know in which stage you are of the VUI
        # TO DO: also, therei s no need to send mp3player to the function. You can give back a response and play audio and do the rest in the main function thread 
        if ((sentence == u"그림") or (sentence == u'painting')):
            rel_path = str(language_code) + '/' + str(paint_mode) + '/general/paint'
            length = int(mp3player.audio_length(rel_path))
            mp3player.play_audio(rel_path)
            keyword_bool = listen_command_while_audio(mp3player, google_voice, language_code, length, keyword_bool)
            
        elif ((sentence == u"화가") or (sentence == u'painter')):
            rel_path = str(language_code) + '/' + str(paint_mode) + '/general/painter'
            length = int(mp3player.audio_length(rel_path))
            mp3player.play_audio(rel_path)
            keyword_bool = listen_command_while_audio(mp3player, google_voice, language_code, length, keyword_bool)
            
        elif ((sentence == u"사용방법") or (sentence == u'instructions')):
            rel_path = str(language_code) + '/' + str(paint_mode) + '/general/explanation_tapping_and_voice_audio'
            length = int(mp3player.audio_length(rel_path))
            mp3player.play_audio(rel_path)
            keyword_bool = listen_command_while_audio(mp3player, google_voice, language_code, length, keyword_bool)
            
        elif ((sentence == u"음악") or (sentence == u"사운드") or (sentence == u"music")):
            rel_path = str(language_code) + '/' + str(paint_mode) + '/general/background_music'
            length = int(mp3player.audio_length(rel_path))
            mp3player.play_audio(rel_path)
            keyword_bool = listen_command_while_audio(mp3player, google_voice, language_code, length, keyword_bool)
            
        elif ((sentence == u"옵션") or (sentence == u'options')):
            rel_path = str(language_code) + '/vui_dialog/help'
            length = int(mp3player.audio_length(rel_path))
            mp3player.play_audio(rel_path)
            keyword_bool = listen_command_while_audio(mp3player, google_voice, language_code, length, keyword_bool)
            
        elif ((sentence == u"끝") or (sentence == u'finish')):
            rel_path = str(language_code) + '/vui_dialog/final_words'
            mp3player.play_audio(rel_path)
            keyword_bool = True
    
        if ((keyword_bool == True) and (sentence)):
            # Free lock to release other thread
            threadLock.release()
            if (DEBUG == 1):
                   print("threadLock released by voice thread")
