#!/usr/bin/env python3
# -*- coding: utf8 -*-

#-------------------------------------------------------------------------------------
# Main program. Needs to be executed with python3 after having changed the parameters file as desired.
#-------------------------------------------------------------------------------------

import sys
import time
import os
import threading
from Mp3player import Mp3player
from MicThread import MicThread
from TappingThread import TappingThread
from GoogleVoice import GoogleVoice
from parameters import *
from MPR121 import MPR121
import wiringpi as wpi


def main():
    """Main program where all the initializations are done and the threads are created and executed. This is the script which needs to be initialized with 
    the command "python3 main.py". If this command is not called first, and is instead imported, this main function will not execute.
    It can also be called as an executable by itself thanks to the sheebang from first line. However, it is recommended to use the command
    aforemention if possible."""
    ##set up: this first variables were originally selected in a menu by the user. Now all the variables need to be changed from the parameters.py file##
    paint_mode = DEFAULT_PAINT
    init_audio_mode = DEFAULT_INITIAL_AUDIO_MODE
    effects_mode = DEFAULT_EFFECT_MODE
    language_code = DEFAULT_LANGUAGE
    interrupt_pin = INTERRUPT_PIN

    #setup wiringPi for the interruption pin from MPR121
    wpi.wiringPiSetup()
    wpi.pinMode(interrupt_pin, 0)

    # Create MPR121 instance.
    cap = MPR121()

    # Initialize communication with MPR121 using default I2C bus of device, and
    # default I2C address (0x5A). 
    if not cap.begin(wpi, interrupt_pin):
        print('Error initializing MPR121.  Check your wiring!')
        sys.exit(1)

    # Initialize google speech client
    google_voice = GoogleVoice(language_code)
              
    # Inititate Mp3player
    mp3player = Mp3player(AUDIOS_PATH, OUTPUT_DEVICE, INPUT_DEVICE)

    # Create new threads and shareable threadLock
    threads = []
    threadLock = threading.Lock()
    tapping_thread = TappingThread("tapping-thread",threadLock, cap, mp3player, paint_mode, language_code)
    voice_thread = MicThread("voice-thread",threadLock, mp3player, google_voice, paint_mode, language_code)
    threads.append(tapping_thread)
    threads.append(voice_thread)

    # Start new Threads
    voice_thread.start()
    tapping_thread.start()
    
    # check for threads termination every 100 ms while the main thread is also running (and checking for the keyboard interrupt (CTL+C).
    # Therefore, once the threads have started running, the program can be stopped by clicking CTL+C. 
    while (len(threads) > 0):
        try:
            threads = [t.join(100) for t in threads if t is not None and t.isAlive()]
        except KeyboardInterrupt:
            # kill whole program
            os.system('kill %d' % os.getpid())

        
if __name__ == '__main__':
    """ if __name__ == '__main__' will also be true if the initial script is this one. The main() will only
    inititates if this program is the one called first with the command "python3 main.py" """
    main()

