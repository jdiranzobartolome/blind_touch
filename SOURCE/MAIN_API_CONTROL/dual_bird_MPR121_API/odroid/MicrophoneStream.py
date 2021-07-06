#!/usr/bin/env python3
# -*- coding: utf8 -*-

#-------------------------------------------------------------------------------------
# Microphone Stream Class (code provided by Google). The original code has been modified for both the following reasons:
#
# 1 - For resetting the microphone listening process before exceeding the maximum time google allows for streaming listening (therefore, by 
#     resetting continuously the system, the sensation of having a microphone listening continuously is accomplished)
# 2-  For accepting a variable "length" which tells the process for how long it should be listening to without giving up and 
#     returning "None". This is mostly used for when the user is listening to an audio so the microphone listens only for 
#     the "stop" and "end" words during that time, returning none if the audio finishes for starting the main VUI prompt again
#     which listens to a different set of words. Separating the microphone listening execution in different modular process
#     which only listen to the needed words improves the reliability of the system as the chances of false positives decrease.   
#-------------------------------------------------------------------------------------


# [START import_libraries]
import pyaudio
import time
from six.moves import queue
from ctypes import *
# [END import_libraries]

##Set up in order to disable all the errors and debugs appearing in console #####
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary('libasound.so')
#Set error handler
asound.snd_lib_error_set_handler(c_error_handler)


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self, audio_init_time, audio_length = 0):
        length = int(audio_length)   
        audio_init_t = audio_init_time

        while not self.closed:
            
            ## if time_out then we return. Which means there is nothing else to iterate over and the google voice algorithm will stop after checking nothing on buffer is the keyword. 
            if ((length != 0) and ((time.time()- audio_init_t) >= length - 1)):
                return
            
            ## Since the maximum streaming audio is 60 seconds, I will make the google speech recognition system return empty and wich code I will make it start again every 14 seconds. (14 seconds because I want it to be short time,
            ## so the voice thread goes out of the function and is able to check often whether the mic should be on or off (since now we have control API). Google charge every audio received as if it was 15 seconds, so 14 seconds seems okay.
            if (((time.time() - audio_init_t) >= 14)):
                return
 
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)
# [END audio_stream]
