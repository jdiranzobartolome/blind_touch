#!/usr/bin/env python3

#-------------------------------------------------------------------------------------
# This is a version of the Adafruit deprecated python library for Adafruit-MPR121
# but with the configuration modified to resemble that one of the C library 
# for the MPR121 by Bare Conductive. The native interrupt pin of the MPR121 is also used
# to improve the performance over the Adafruit original library. Besides that, a function 
# for recognizing double and triple tapping has being added. The configuration of the MPR121 
# is really important and changes the latency and accuracy of the tactile response hugely. 
# The current configuration works great for our goals but if a case in which the tactile performance 
# is not satisfactory the following steps should be followed iteratively checking after each step
# whether the desired resuls are reached. (TO DO) 
#
#    1 - Change touch and release threshold from the parameters.py file. 
#        Never make the release threshold smaller than the touch threshold.
#    2 - 
#
#
# Similarly, if there is a problem with the tapping recognition, the variables 
# FASTEST_TAPPING_INTERVAL (default of 0.1) and SLOWEST_TAPPING_INTERVAL (default 0.4)
# need to be modified. 

# Author: Jorge David Iranzo
#-------------------------------------------------------------------------------------

# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import time
from parameters import *

# Register addresses. The default value of the configuration registers is shown next to them.               
MPR121_I2CADDR_DEFAULT = 0x5A
MPR121_TOUCHSTATUS_L   = 0x00
MPR121_TOUCHSTATUS_H   = 0x01
MPR121_FILTDATA_0L     = 0x04
MPR121_FILTDATA_0H     = 0x05
MPR121_BASELINE_0      = 0x1E   
MPR121_MHDR            = 0x2B             # 0x01
MPR121_NHDR            = 0x2C             # 0x01
MPR121_NCLR            = 0x2D             # 0x10
MPR121_FDLR            = 0x2E             # 0x20
MPR121_MHDF            = 0x2F             # 0x01
MPR121_NHDF            = 0x30             # 0x01
MPR121_NCLF            = 0x31             # 0x10
MPR121_FDLF            = 0x32             # 0x20
MPR121_NHDT            = 0x33             # 0x01
MPR121_NCLT            = 0x34             # 0x10
MPR121_FDLT            = 0x35             # 0xFF
MPR121_TOUCHTH_0       = 0x41             # touch threshold: all electrodes (default: 40)
MPR121_RELEASETH_0     = 0x42             # release threshold: all electrodes(default: 20)
MPR121_DEBOUNCE        = 0x5B             # 0x11
MPR121_CONFIG1         = 0x5C             # 0xFF
MPR121_CONFIG2         = 0x5D             # 0x30
MPR121_MHDPROXR        = 0x36;            # 0x0F
MPR121_NHDPROXR        = 0x37;            # 0x0F
MPR121_NCLPROXR        = 0x38;            # 0x00
MPR121_FDLPROXR        = 0x39;            # 0x00
MPR121_MHDPROXF        = 0x3A;            # 0x01
MPR121_NHDPROXF        = 0x3B;            # 0x01
MPR121_NCLPROXF        = 0x3C;            # 0xFF
MPR121_FDLPROXF        = 0x3D;            # 0xFF
MPR121_NHDPROXT        = 0x3E;            # 0x00
MPR121_NCLPROXT        = 0x3F;            # 0x00
MPR121_FDLPROXT        = 0x40;            # 0x00
MPR121_CHARGECURR_0    = 0x5F
MPR121_CHARGETIME_1    = 0x6C
MPR121_ECR             = 0x5E             # 0xCC
MPR121_AUTOCONFIG0     = 0x7B             # 0x00  
MPR121_AUTOCONFIG1     = 0x7C             # 0x00
MPR121_UPLIMIT         = 0x7D             # 0x00
MPR121_LOWLIMIT        = 0x7E             # 0x00
MPR121_TARGETLIMIT     = 0x7F             # 0x00
MPR121_GPIODIR         = 0x76
MPR121_GPIOEN          = 0x77
MPR121_GPIOSET         = 0x78
MPR121_GPIOCLR         = 0x79
MPR121_GPIOTOGGLE      = 0x7A
MPR121_SOFTRESET       = 0x80

MAX_I2C_RETRIES = 5

class MPR121(object):
    """Representation of a MPR121 capacitive touch sensor."""

    def __init__(self):
        """Create an instance of the MPR121 device."""
        # Nothing to do here since there is very little state in the class.
        pass

    def begin(self, wiringPi, interrupt_pin, address=MPR121_I2CADDR_DEFAULT, i2c=None, **kwargs):
        """Initialize communication with the MPR121. 
        Can specify a custom I2C address for the device using the address 
        parameter (defaults to 0x5A). Optional i2c parameter allows specifying a 
        custom I2C bus source (defaults to platform's I2C bus). Besides, the wiringPi setup object
        and the number of wiringPi pin which wants to be used for reading the interruption need be
        specified.

        Returns True if communication with the MPR121 was established, otherwise
        returns False. 
        """        
        # Assume we're using platform's default I2C bus if none is specified.
        if i2c is None:
            import Adafruit_GPIO.I2C as I2C
            i2c = I2C
            # Require repeated start conditions for I2C register reads.  Unfortunately
            # the MPR121 is very sensitive and requires repeated starts to read all
            # the registers.
            I2C.require_repeated_start()
        # Save a reference to the I2C device instance for later communication.
        self._device = i2c.get_i2c_device(address, **kwargs)
        self.touched_data = 0
        self.last_touched_data = 0
        #self.auto_touch_status_flag is not used yet. It is useful if adding more code
        #so it can be use as a variable to know if the status flag is being changed
        # while we are focusing in other process (as a way of checking the IQR offen) 
        self.auto_touch_status_flag = False   
        self.interrupt_pin = interrupt_pin
        self.wiringPi = wiringPi
        return self._reset()

    def _reset(self):
        # Soft reset of device.
        self._i2c_retry(self._device.write8, MPR121_SOFTRESET, 0x63)
        time.sleep(0.001) # This 1ms delay here probably isn't necessary but can't hurt.
        # Set electrode configuration to default values.
        self._i2c_retry(self._device.write8, MPR121_ECR, 0x00)
        # Check CDT, SFI, ESI configuration is at default values.
        c = self._i2c_retry(self._device.readU8, MPR121_CONFIG2)
        if c != 0x24:
           return False
        # Set threshold for touch and release to default values.
        self.set_thresholds(MPR121_TOUCH_THRESHOLD, MPR121_RELEASE_THRESHOLD)
        # Configure baseline filtering control registers.
        self._i2c_retry(self._device.write8, MPR121_MHDR, 0x01)
        self._i2c_retry(self._device.write8, MPR121_NHDR, 0x01)
        self._i2c_retry(self._device.write8, MPR121_NCLR, 0x10)
        self._i2c_retry(self._device.write8, MPR121_FDLR, 0x20)
        self._i2c_retry(self._device.write8, MPR121_MHDF, 0x01)
        self._i2c_retry(self._device.write8, MPR121_NHDF, 0x01)
        self._i2c_retry(self._device.write8, MPR121_NCLF, 0x10)
        self._i2c_retry(self._device.write8, MPR121_FDLF, 0x20)
        self._i2c_retry(self._device.write8, MPR121_NHDT, 0x01)
        self._i2c_retry(self._device.write8, MPR121_NCLT, 0x10)
        self._i2c_retry(self._device.write8, MPR121_FDLT, 0xFF)
        #added by me since they are in the bare conductive configuration
        self._i2c_retry(self._device.write8, MPR121_MHDPROXR, 0x0F)
        self._i2c_retry(self._device.write8, MPR121_NHDPROXR, 0x0F)
        self._i2c_retry(self._device.write8, MPR121_NCLPROXR, 0x00)
        self._i2c_retry(self._device.write8, MPR121_FDLPROXR, 0x00)
        self._i2c_retry(self._device.write8, MPR121_MHDPROXF, 0x01)
        self._i2c_retry(self._device.write8, MPR121_NHDPROXF, 0x01)
        self._i2c_retry(self._device.write8, MPR121_NCLPROXF, 0xFF)
        self._i2c_retry(self._device.write8, MPR121_FDLPROXF, 0xFF)
        self._i2c_retry(self._device.write8, MPR121_NHDPROXT, 0x00)
        self._i2c_retry(self._device.write8, MPR121_NCLPROXT, 0x00)
        self._i2c_retry(self._device.write8, MPR121_FDLPROXT, 0x00)

        # Set other configuration registers.
        self._i2c_retry(self._device.write8, MPR121_DEBOUNCE, 0x11)
        self._i2c_retry(self._device.write8, MPR121_CONFIG1, 0xFF) 
        self._i2c_retry(self._device.write8, MPR121_CONFIG2, 0x30) 
        # Enable all electrodes.
        self._i2c_retry(self._device.write8, MPR121_ECR, 0xCC)
        # All done, everything succeeded!
        return True

    def _i2c_retry(self, func, *params):
        # Run specified I2C request and ignore IOError 110 (timeout) up to
        # retries times.  For some reason the Pi 2 hardware I2C appears to be
        # flakey and randomly return timeout errors on I2C reads.  This will
        # catch those errors, reset the MPR121, and retry.
        count = 0
        while True:
            try:
                return func(*params)
            except IOError as ex:
                # Re-throw anything that isn't a timeout (110) error.
                if ex.errno != 110:
                    raise ex
            # Else there was a timeout, so reset the device and retry.
            self._reset()
            # Increase count and fail after maximum number of retries.
            count += 1
            if count >= MAX_I2C_RETRIES:
                raise RuntimeError('Exceeded maximum number or retries attempting I2C communication!')

    def set_thresholds(self, touch, release):
        """Set the touch and release threshold for all inputs to the provided
        values.  Both touch and release should be a value between 0 to 255
        (inclusive).
        """
        assert touch >= 0 and touch <= 255, 'touch must be between 0-255 (inclusive)'
        assert release >= 0 and release <= 255, 'release must be between 0-255 (inclusive)'
        # Set the touch and release register value for all the inputs.
        for i in range(12):
            self._i2c_retry(self._device.write8, MPR121_TOUCHTH_0 + 2*i, touch)
            self._i2c_retry(self._device.write8, MPR121_RELEASETH_0 + 2*i, release)

    def filtered_data(self, pin):
        """Return filtered data register value for the provided pin (0-11).
        Useful for debugging.
        """
        assert pin >= 0 and pin < 12, 'pin must be between 0-11 (inclusive)'
        return self._i2c_retry(self._device.readU16LE, MPR121_FILTDATA_0L + pin*2)

    def baseline_data(self, pin):
        """Return baseline data register value for the provided pin (0-11).
        Useful for debugging.
        """
        assert pin >= 0 and pin < 12, 'pin must be between 0-11 (inclusive)'
        bl = self._i2c_retry(self._device.readU8, MPR121_BASELINE_0 + pin)
        return bl << 2

    def touched(self):
        """Return touch state of all pins as a 12-bit value where each bit 
        represents a pin, with a value of 1 being touched and 0 not being touched.
        """
        t = self._i2c_retry(self._device.readU16LE, MPR121_TOUCHSTATUS_L)
        return t & 0x0FFF

    def is_touched(self, pin):
        """Return True if the specified pin is being touched, otherwise returns
        False.
        """
        assert pin >= 0 and pin < 12, 'pin must be between 0-11 (inclusive)'
        t = self.touched()
        return (t & (1 << pin)) > 0
    
    def touch_status_changed(self):
        """Return True if the status of the pins have changed. It mostly works by reading the interruption pin
        self.auto_touch_status_flag is a variable which can be used in the code to force the status changed
        in case it is needed."""
        return (self.auto_touch_status_flag or (not self.wiringPi.digitalRead(self.interrupt_pin)))

    def update_touch_data(self):
        """ update the touch information (self.touched_data and self.last_touched_data variables are updated"""
        self.auto_touch_status_flag = False
        self.last_touched_data = self.touched_data
        self.touched_data = self.touched()
    
    def get_num_touched(self):
        """ return the number of zones which are being touched by the user """
        return bin(self.touched_data).count("1")

    def is_new_touch(self, pin):
        """ given a pin, it returns True if the pin has been touched and False if it has been release or have not changed """
        assert pin >= 0 and pin < 12, 'pin must be between 0-11 (inclusive)'
        t = self.last_touched_data ^ self.touched_data
        return (((t & (1 << pin)) > 0) and ((self.touched_data & (1 << pin)) > 0 ))

    def is_new_release(self, pin):
        """ given a pin, it returns True if the pin has been released and False if it has been touched or have not changed """
        assert pin >= 0 and pin < 12, 'pin must be between 0-11 (inclusive)'
        t = self.last_touched_data ^ self.touched_data
        return (((t & (1 << pin)) > 0) and ((self.last_touched_data & (1 << pin)) > 0))

    def is_tapping_any_finger_zone(self):
        """Wait for a tapping of 2 or 3 hits. It returns the number of taps (either 2 or 3).
        In this case the tapping is read regardless of how many zones are being touched at
        the same time.  
        
        ----TO DO----
        """
    
    def is_tapping_one_finger_zone(self, length = 0):
        """Wait for a tapping of 2 or 3 hits. It returns the number of taps (either 2 or 3).
        In this case the tapping is read when only one finger is tapping one of the zones at
        a time. If several zones are touched or during the tapping process other zone is touched, 
        the tapping gets cancelled. 
        """
        last_touched = 0
        touch_events = [0 for x in range(12)] 
        last_tap = 0
        t_last_tapping_event = 0
        audio_length = int(length)
        init_time = time.time()

        while True:
            if self.touch_status_changed():
                self.update_touch_data()
                if (DEBUG == 1):
                    print('status changed!')
                if self.get_num_touched() == 1:
                    for i in range(12):
                        if self.is_new_touch(i):
                            if (DEBUG == 1):
                                print('pin ' + str(i) + 'touched')  
                            if ((touch_events[i] == 0) or ((time.time() - last_tap) < SLOWEST_TAPPING_INTERVAL) and (time.time()-last_tap > FASTEST_TAPPING_INTERVAL)):
                                last_tap = time.time()
                                if (i != last_touched):
                                    touch_events[last_touched] = 0
                                touch_events[i] += 1
                                last_touched = i
                        elif self.is_new_release(i):
                            if (DEBUG == 1):
                                print('pin ' + str(i) + 'released')

            #code which iteratively checks whether a tapping event has taken place. The times are needed to give the chance to the user
            #to tap for the third time after having tapped twice.
            if (((time.time() - last_tap) < 0.7) and ((time.time() - last_tap) > SLOWEST_TAPPING_INTERVAL) and (touch_events[last_touched]==2) and ((time.time() - t_last_tapping_event) > 1.5)):
                if (TAPPING_FEEDBACK == 1):
                    print("double tapping event")
                touch_events[last_touched] = 0
                t_last_tapping_event = time.time()
                return last_touched, 2
            elif (((time.time() - last_tap) < 0.7) and ((time.time() - last_tap) > SLOWEST_TAPPING_INTERVAL) and (touch_events[last_touched]==3) and ((time.time() - t_last_tapping_event) > 1.5)):
                if (TAPPING_FEEDBACK == 1):
                    print("triple tapping event")
                touch_events[last_touched] = 0
                t_last_tap = time.time()
                return last_touched, 3
            elif (time.time() - last_tap > 0.7):
                touch_events[last_touched] = 0
            
            elif ((audio_length != 0) and ((time.time() - init_time) > audio_length)):
                if (TAPPING_FEEDBACK == 1):
                    print("audio file finished without cancelling it by tapping. returned None, None from MPR121 tapping function")
                return None, None




            
                
                
        
        
