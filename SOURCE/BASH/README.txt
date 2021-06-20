

if you find out the microphone is not being recognized by pulseaudio the following steps need to be performed:
 
  1 - check with the command "arecord -l" if alsa recognizes the device. If it appears there, 
      check the number of card and the number of device, which is shown by the command. If it does not appear,
	  some drivers might be needed for the device to be recognized by the linux kernel.
	  
  2 - If it is recognized by alsa, execute the file "mic_recognition.sh" as superuser 
      and with the card and device numbers as first and second parameter.
	    ex:"sudo ./mic_recognition.sh 0 1" 
  
  3 - try again the program to check whether now the microphone is being recognized. 

We recommend to undo the changes done by the mic_recognize file from time to time.
For undoing any kind of change that has been done to the pulseaudio configuration by using the 
mic_recognize.sh file, run the command: 

# sudo sed -i '/##line added by mic_recognize.sh for solving mic recognition error by pyaudio (delete it if not needed anymore)/,+2 d'