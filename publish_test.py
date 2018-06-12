"""This script reads from different ADC inputs at three established frequencies,
stores that data in three different files (one for each frequency)
and sends the three files over to the Mosquitto server, each one published 
at a different topic ('RasPi1/1Hz',' RasPi1/10Hz', 'RasPi1/100Hz')
"""

from datetime import datetime
import Adafruit_ADS1x15
import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np
import time

#create an mqtt client instance
mqttc = mqtt.Client("python_pub")
#connect to the Google Cloud Mosquitto broker
mqttc.connect("35.237.36.219", 1883)

# create three ADS115 instances 
adc0 = Adafruit_ADS1x15.ADS1115(0x48) # ADR to GRN
adc1 = Adafruit_ADS1x15.ADS1115(0x49) # ADR to VDD
adc2 = Adafruit_ADS1x15.ADS1115(0x4A) # ADR to SDA
adc3 = Adafruit_ADS1x15.ADS1115(0x4B) # ADR to SCL


GAIN = 1 # We are going to use same gain for all of them

"""Three different functions reading data at the three 
different chosen intervals (1Hz, 10Hz and 100Hz)"""

#Function reads all channels from first two (0, 1) adc's at 10Hz
def read_ten_hz():
    while True:
        header = ['adc', 'channel', 'time_stamp', 'value']
        values = np.array([0, 0, np.datetime64(datetime.now()), 0])
        for i in range(600):
            #Time measurement to know how long this procedure takes
            now = time.time()

            values = np.vstack((values, np.array([0, 0, np.datetime64(datetime.now()), adc0.read_adc(0, gain=GAIN)])))
            values = np.vstack((values, np.array([0, 1, np.datetime64(datetime.now()), adc0.read_adc(1, gain=GAIN)])))
            values = np.vstack((values, np.array([0, 2, np.datetime64(datetime.now()), adc0.read_adc(2, gain=GAIN)])))
            values = np.vstack((values, np.array([0, 3, np.datetime64(datetime.now()), adc0.read_adc(3, gain=GAIN)])))
            values = np.vstack((values, np.array([1, 0, np.datetime64(datetime.now()), adc1.read_adc(0, gain=GAIN)])))
            values = np.vstack((values, np.array([1, 1, np.datetime64(datetime.now()), adc1.read_adc(1, gain=GAIN)])))
            values = np.vstack((values, np.array([1, 2, np.datetime64(datetime.now()), adc1.read_adc(2, gain=GAIN)])))
            values = np.vstack((values, np.array([1, 3, np.datetime64(datetime.now()), adc1.read_adc(3, gain=GAIN)])))

            operation_time = time.time()-now

            if operation_time > 0.1:
                time.sleep(0.1)
            else:
                time.sleep(0.1 - operation_time)

        dataframe = pd.DataFrame(values, columns=header)
        dataframe.to_csv('ten_hz.csv', columns=header, index=False)
        f = open('ten_hz.csv')
        csv = f.read()
        mqttc.publish("RasPi1/10Hz", csv, 2)

read_ten_hz()

#Creation of threads to run in parallel


#Executing threads at same time

"""while True:
    # Read the specified ADC channel
    value = adc0.read_adc(0, gain=GAIN)

    print('Channel 0: {0}'.format(value))
    
    #Publish data to our broker
    mqttc.publish("test/one", str(value))

    # Sleep for half a second.
    time.sleep(0.5)

mqttc.loop_forever()"""
