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

broker = "35.237.36.219" # static IP of mosquitto broker
port = 1883
GAIN = 1 # We are going to use same gain for all of them

# create three ADS115 instances 
adc0 = Adafruit_ADS1x15.ADS1115(0x48) # ADR to GRN
adc1 = Adafruit_ADS1x15.ADS1115(0x49) # ADR to VDD
adc2 = Adafruit_ADS1x15.ADS1115(0x4A) # ADR to SDA
adc3 = Adafruit_ADS1x15.ADS1115(0x4B) # ADR to SCL

def read_ten_hz():
    """ 
    Function that reads from all channels from first two (0, 1) adc's
    ten times in a second, creates a numpy array which is then converted to a
    panda's dataframe and into a CSV file and sent to the MQTT broker with the 
    topic RasPi1/10Hz
    """
    client1 = mqtt.Client("ten_hz") #create an mqtt client instance
    client1.on_publish = on_publish #assign function callback
    client1.connect(broker, port) #establish connection to the Mosquitto broker
    # Function for clients1's specific callback when pubslishing message
    def on_publish(client, userdata, result):
        print("Data Published")
        pass
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

            if operation_time < 0.1:
                time.sleep(0.1 - operation_time)
                
        dataframe = pd.DataFrame(values, columns=header)
        dataframe.to_csv('ten_hz.csv', columns=header, index=False)
        f = open('ten_hz.csv')
        csv = f.read()
        client1.loop_start()
        client1.publish("RasPi1/10Hz", csv, 2)
        client1.loop_stop()

if __name__ == '__main__':
    read_ten_hz()