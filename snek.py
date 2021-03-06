#!/bin/usr/python3
# -*- coding: utf-8 -*-

'''
Created on Sat Jan 16 03:29:51 2021
snek.py

A control loop script for monitoring and controlling environemental conditions
in a household terrarium using a Raspberry Pi. Classes are designed to be
modular and easily extensible in the event that additonal hardware is installed
at a later date.

For Piper.

@author: Tyler King
'''

import time
import RPi.GPIO as gpio

#Parameters and settings
#These will need to be changed to the appropriate values once the relevant
#devices are properly attached
#-----------------------------
temperature_monitor_pin = 1     #Pin number for temperature probe
temperature_control_pin = 26     #Pin number for temperature control mechanism
humidity_monitor_pin = 3        #Pin number for humidity probe
humidity_control_pin = 21        #Pin number for humidity control mechanism
light_control_pin = 20           #Pin number for light control mechanism

min_temperature = 89            #Minimum temperature to be allowed by temperature controller, in degrees Farenheit
max_temperature = 91            #Maximum temperature to be allowed by temperature controller, in degrees Farenheit
min_humidity = 40               #Minimum humdity to be allowed by humidity controller (in %humidity)
max_humidity = 70              #Maximum humdity to be allowed by humidity controller (in %humidity)
light_cycle_time = 12           #Cycle time for lights, in hours. Lights will cycle on/off every light_cycle_time hours
sample_frequency = 60           #Frequency at which tank conditions are tested, in seconds
#-----------------------------

check_elapsed_time = lambda t0: time.time() - t0

class BinaryController:
    '''
    Generalized handle for interacting with binary digital I/O devices.

    Attributes:
    ------------
    channel, int: The pinout number of the control pin for the light(s)
    state, bool: the current state of the light(s) controlled by the pin
    parameters, dict: Just a dictionary for miscellaneous metadata

    Methods:
    ------------
    turnOn: sets state to True and turns on any connected devices

    turnOff: sets state to False and turns off any connected devices
    '''

    def __init__(self, channel, **kwds):
        self.channel = channel
        self.state = False
        self.parameters = dict(kwds)
        self.turnOff()

    def turnOn(self):
        self.state = True
        gpio.output(self.channel, gpio.HIGH)

    def turnOff(self):
        self.state = False
        gpio.output(self.channel, gpio.LOW)

class TemperatureMonitor:
    '''
    Helper class for interacting with temperature probe.

    Attributes:
    -------------
    channel, int: The pinout number of the data/control pin for the temperature probe

    Methods:
    -------------
    measure: measure current temperature, returns measured temperature as a float
    '''

    def __init__(self):
        return

    def measure(self):
        '''
        Obtains a single temperature measurement from the attached probe, returns
        the measured humidity as an int in degrees Farenheit.

        Note: The actual code here will vary depending on exactly which humidity
        probe you use. I recommend the DHT11 since it combines a humidity
        sensor and thermometer into a single package. However, the
        measurements on the DHT11 tend to be very noisy so it may be worth it to
        inverst in a better probe, especially since it's going to be keeping a
        pet alive. I could alternatively write a more robust measurement
        function that uses the average of several measurements to counteract
        some of the noise of the DHT11. We can play it by ear.
        '''
        return

class HumidityMonitor:
    '''
    Helper class for interacting with humidity probe.

    Attributes:
    ------------
    Methods:
    ------------
    '''

    def __init__(self, channel):
        self.channel = channel
        return

    def measure(self):
        '''
        Obtains a single humidity measurement from the attached probe, returns
        the measured humidity as an int with units %humidity.

        Note: Like the TemperatureMonitor.measure function, the exact code here
        will depend on which humidity probe you end up using.
        '''
        return

if __name__ == '__main__':
    #Specify pin numbering system (either "BOARD" or "BCM")
    gpio.setmode(gpio.BOARD)

    #Initialize GPIO pins
    gpio.setup(temperature_monitor_pin, gpio.IN)
    gpio.setup(temperature_control_pin, gpio.OUT)
    gpio.setup(humidity_monitor_pin, gpio.IN)
    gpio.setup(humidity_control_pin, gpio.OUT)
    gpio.setup(light_control_pin, gpio.OUT)

    #Initialize devices and set to their default states
    temp_probe = TemperatureMonitor(temperature_monitor_pin)
    temp_control = BinaryController(temperature_control_pin)
    humidity_probe = HumidityMonitor(humidity_monitor_pin)
    humidity_control = BinaryController(humidity_control_pin)
    light_control = BinaryController(light_control_pin)

    #Initialize timers
    last_check = time.time()
    light_timestamp = time.time()

    #Begin main loop
    while True:
        elapsed_time = check_elapsed_time(last_check)
        if elapsed_time >= sample_frequency:
            #Update sampling timer
            last_check = time.time()

            #Measure temperature and humidity
            temperature = temp_probe.measure()
            humidity = humidity_probe.measure()

            #Evaluate measured temperature and humidity
            #If measured value(s) outside of set range, make appropriate response
            if temperature <= min_temperature and temp_control.state == False:
                temp_control.turnOn()
            elif temperature >= max_temperature and temp_control.state == True:
                temp_control.turnOff()
            else:
                pass

            if humidity <= min_humidity and humidity_control.state == False:
                humidity_control.turnOn()
            elif humidity >= max_humidity and humidity_control.state == True:
                humidity_control.turnOff()
            else:
                pass

            #Check light timer, switch on/off if expired
            light_time = check_elapsed_time(light_timestamp)
            if light_time > light_cycle_time:
                if light_control.state == False:
                    light_control.turnOn()
                else:
                    light_control.turnOff()

        else:
            #If sample frequency time has not elapsed, wait 1 second and check again
            time.sleep(1)
