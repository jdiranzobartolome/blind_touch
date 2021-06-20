

if [ "$#" -ne 2 ]; then
    echo "Illegal number of parameters. Please, read the README.txt file before executing this one."
fi

# undoing old changes in pulseaudio.pa file. 
sudo sed -i \
'/##line added by mic_recognize.sh for solving mic recognition error by pyaudio (delete it if not needed anymore)/,+2 d'\
/etc/pulse/default.pa

# add the necessary line to the pulseaudio.pa file
sudo sed .i '/match/i \
##line added by mic_recognize.sh for solving mic recognition error by pyaudio (delete it if not needed anymore)\
load-module module-alsa-source device=hw:${1},${0}
## end of the line added by external program mic_recognize.sh' \
/etc/pulse/default.pa

pulseaudio -k ; pulseaudio -D



## CHECK WHETHER THE DEFAULT.PA FILE GETS RESETED WHEN BOOTING OR IF THE WRITTEN LINE WILL BE THERE FOREVER.... :S. If show, make a different
## script explaiend in the readme file that tells the user to run it when they will not use the microphone anymore to 
## automatically delete it from the default configuration file of pulse audio. 

## You could also do this!: make an exception in python if the input device is not recognized, if that exception arises you tell the user
## to read the readme of this file and use this. 