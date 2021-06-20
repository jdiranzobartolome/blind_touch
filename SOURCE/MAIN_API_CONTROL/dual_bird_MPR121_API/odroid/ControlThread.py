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

from flask import Flask
from flask_restful import Api, Resource, reqparse
import threading
import time
import os
from parameters import *

exitFlag = 0

class ControlThread (threading.Thread):
   """Representation of the Restful API control function thread"""

   def __init__(self, name, q_voice):
      """Create an instance of the thread."""
      threading.Thread.__init__(self)
      self.name = name
      self.q_voice = q_voice
      
   def run(self):
      """Starts execution of the thread"""
      print ("Starting " + str(self.name))
      control_thread_main( self.q_voice)
      print ("Exiting " + str(self.name))


def control_thread_main(q_voice):
    """ Ex"""
    # I like defining this kind of things in main (even if I have to send them to the thread class afterwards
    # but since the API is not always on and I need to use (if API=0n)... I will try to polute the original code as little as possible
    app = Flask(__name__)  #CAREFUL WITH THIS, WONDER IF IT WILL FAIL BECAUSE THIS IS NOT THE INITIAL SCRIPT, REMEMBER THIS!
    api = Api(app)
    print("configurando API")

    #I create the only resource and the only instance possible. Every value receive will be automatically sent to the neighbour threads, so 
    #no need for database nor anything like that. 
    configuration = {"mic": "on", "volume": "50", "restart": "no"}
    
    class Configuration(Resource):
        
        # there is no option for 404 error, there is only an instance, it will always be found
        def get(self):
            return configuration, 200
        
        #a "default" gives the default values of that parameter
        def put(self): 
            parser = reqparse.RequestParser()
            parser.add_argument("mic")
            parser.add_argument("mic_state")
            parser.add_argument("volume")
            parser.add_argument("restart")
            args = parser.parse_args()
            print(args)
            
            if (args["restart"]):
               if (args["restart"] == "yes"):
                   os.execv(os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py")),["main.py"])
            if (args["mic"]):
                configuration["mic"] = args["mic"]
                #sharing with the voice thread
                if args["mic"]:
                   if (args["mic"] == "default"):
                       q_voice.put("on")
                   elif ((args["mic"] == "on") or (args["mic"] == "off")):
                       q_voice.put(args["mic"])
            if (args["volume"]):
                configuration["volume"] = args["volume"]
                #chnging volume levels
                if (args["volume"]):
                    if (args["volume"] == "default"):
                        pass
                    else:
                        pass

            return configuration, 200
            
        #NOTA!! El reset se lo puedo enviar al main y que el mismo reinicie los threads o algo asi
    api.add_resource(Configuration, "/configuration")
    print(" iniciando API")
    #listen in 0.0.0.0 (all interfaces) and in a port highet than 2014 (non-high priviledged ports, so sudo is not needed to listen on those)
    app.run(host= '0.0.0.0', port="5000", debug=False)        
    #Only use the version with debug=True when there are errors and never in production setting
    app.run(host= '0.0.0.0', port="5000", debug=True, use_reloader = False)
 
