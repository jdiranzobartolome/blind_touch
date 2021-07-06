#!/usr/bin/env python3
# -*- coding: utf8 -*-

#-------------------------------------------------------------------------------------
# Google API client class. It is based mostly on one of the example codes provided by google. 
# Changes have been made so the variable "length" could be use to exit the process earlier after
# some "length" amount of seconds passed. It also allows for a language variable in __init__ and a 
# keyword_boolean in the function "listen_command" in order to know which language and which set of 
# keywords from that language we are listening to. It is important to remember that the function 
# "streaming_recognize" starts a generator (python iterator functions which end up in a "yield"
# command instead of in a "return". The iterator makes the streaming process more complex so any change
# should be made carefully. 
#-------------------------------------------------------------------------------------


# [START import_modules]

import time
import re
import os
import sys
from parameters import *
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import MicrophoneStream
from parameters import *

# [START import_modules]

class GoogleVoice:
    """Class which sets up the google client and the environment"""
    def __init__(self, language_code):
        self.language_code = language_code
        self.keys = os.environ.keys()
        from re import search
        for key in self.keys:
            if not search("MY_PATH", key):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= APIKEY_PATH
  
        self.client = speech.SpeechClient()
        config = types.RecognitionConfig( 
                           encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                           sample_rate_hertz=RATE, language_code=language_code)
        self.streaming_config = types.StreamingRecognitionConfig(config=config, 
                                                        interim_results=True)
                                                    
    
    def listen_command(self, keyword_bool, audio_length = 0):
        """Class which sets up the google client and the environment. If "audio_length" is received (so it is different than 0) that
        means that we the user is listening to an audio and we only care about "stop" and "end" commands. If by the time the audio finishes 
        none of those commands have been said by the user, the the mic stops listening and keeps executing the main program. """
        
        # we calculate current time (approximate time at which the audio starts)
        audio_init_time = time.time()
        
        with MicrophoneStream.MicrophoneStream(RATE, CHUNK) as stream:     
            audio_generator = stream.generator(audio_init_time, audio_length)

            requests = (types.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)      
        ####Uncomment if this sound wants to be implemmented
        #if we are ready to listen to the real commands because the keyword has been listened to, then we give a cue to the user with a sound.
        # I commented it because now there is a VUI so the user knows the mic listened thanks to the voiced answer.
        # if (keyword_bool == false): 
            # time.sleep(0.1) #para que suene el pitido ya que daba problemas cuando hecho por solo consola headless
            # os.system('mpg321 -l 3 ../audioskorean/bips/beep-29.mp3 > /dev/null 2>&1 &')
            responses = self.client.streaming_recognize(self.streaming_config, requests)
       
            #function that print the results and exit if keyword appears
            transcript = listen_print_loop(responses, self.language_code, keyword_bool, audio_length)
             
        if (transcript):
            command = transcript.replace(u" ",u"")
        else:
            command = "" 
    
        return command
    
    
#----------------------------------------------------------------#
## function for transcribing and checkiong for keywords ##
 
def listen_print_loop(responses, language_code, keyword_bool, audio_length):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """

    # set up del printed_chars y de la reg expression
    num_chars_printed = 0
    if (keyword_bool == True):
        my_regex = r"\b%s\b"%KEY_WORD[language_code]
    elif (audio_length != 0):
        my_regex = r"\b%s\b"%KEY_STOP[language_code]
    else:
         my_regex = r"\b%s\b"%KEY_PHRASES[language_code]
    #my_regex_utf8 = my_regex.decode('utf-8')     ##Not needed in the python3 but remember, in python2 this would be needed
    my_regex_utf8 = my_regex
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript
        
        # Checking whether one of the words is a keyword. By being done here, not checking wheter 'result.is_final'. 
        # Therefore, we make sure that the word is accepted even in the middle of sentences which improves latency.
        match = re.search(my_regex_utf8, transcript, re.I)
        if match:
             print('Exiting..')
             return match.group(0)
             #break
         
        if (VOICE_FEEDBACK == 1):
            ### Display interim results, but with a carriage return at the end of the
            ### line, so subsequent lines will overwrite them.
            ### If the previous result was longer than this one, we need to print
            ### some extra spaces to overwrite the previous result
            overwrite_chars = ' ' * (num_chars_printed - len(transcript))
            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + '\r')
                sys.stdout.flush()
                num_chars_printed = len(transcript)
            else:
                print(transcript + overwrite_chars)

        ## Another way of exiting. After doing result.is_final, so the word will only be accepted if it is considered final.
        ## Do not delete this in case it is needed in the future
          ##Exit recognition if any of the transcribed phrases could be
          ##one of our keywords.
          ##match belongs to class re.MatchObject (https://docs.python.org/3.1/library/re.html#re.MatchObject)
         #match = re.search(my_regex_utf8, transcript, re.I)     
         #if match:
             #print('Exiting..')
             #return match.group(0)
             #break
