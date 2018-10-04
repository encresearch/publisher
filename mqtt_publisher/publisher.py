"""
This script reads from different Analog to Digital Converters (ADC) 
inputs at three established frequencies. It runs two processes at the same time.
They collect data from the first two, and last two ADCs respectively, writes it to a
CSV file, and then sends it to a Mosquitto broker on the cloud.

The devices' GAIN was chosen to be 1. Since this is a 16 bits device, the measured
voltage will depend on the programmable GAIN. The following table shows the possible
reading range per chosen GAIN. A GAIN of 1 goes from -4.096V to 4.096V.
- 2/3 = +/-6.144V
-   1 = +/-4.096V
-   2 = +/-2.048V
-   4 = +/-1.024V
-   8 = +/-0.512V
-  16 = +/-0.256V

This means that the maximum range of this 16 bits device is +/-32767.
Thus, to convert bits to V, we divide 4.096 by 32767,
which gives us 0.000125. In conclusion, to convert this readings to mV
we just need to multiply the output times 0.125, which is done in the server
side (mqtt-connector) to prevent time delays.
"""

from datetime import datetime
import Adafruit_ADS1x15
import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np
import time
from multiprocessing import Process

# create four ADS115 instances with different addresses
# based on the connection of the ADR (address) pin
# Data Rate samples are chosen based on the frequency we want to pull data
# from it. data_rate indicates the time it will take in measuring the analog data
adc0 = Adafruit_ADS1x15.ADS1115(address=0x48) # ADR to GRN | Will do 10Hz readings
adc1 = Adafruit_ADS1x15.ADS1115(address=0x49) # ADR to VDD | Will do 10Hz readings
adc2 = Adafruit_ADS1x15.ADS1115(address=0x4A) # ADR to SDA | Will do 1Hz readings
adc3 = Adafruit_ADS1x15.ADS1115(address=0x4B) # ADR to SCL | Will do 100Hz readings

def connect_to_broker(client_id, host, port, keepalive, on_connect, on_publish):
    # Params -> Client(client_id=””, clean_session=True, userdata=None, protocol=MQTTv311, transport=”tcp”)
    # We set clean_session False, so in case connection is lost, it'll reconnect with same ID
    client = mqtt.Client(client_id=client_id, clean_session=False)
    client.on_connect = on_connect
    client.on_publish = on_publish
    connection = client.connect(host, port, keepalive)
    return (client, connection)

def read_ten_hz():
    """ 
    Reads from all channels from first two (0, 1) adc's ten times in a second, 
    creates a numpy array which is then converted to a panda's dataframe and into a CSV file
    and sent to the MQTT broker with topic RasPi1/10Hz
    """
    client_id = "TEN_HZ"
    host = "35.237.36.219" # static IP of mosquitto broker
    port = 1883
    keepalive = 30
    topic = "usa/quincy/1"
    GAIN = 1 # We are going to use same gain for all of them
    headers = ['adc', 'channel', 'time_stamp', 'value'] # Headers of the upcoming csv file
    data_rate = 475
    def on_connect(client, userdata, flags, rc):
        pass

    def on_publish(client, userdata, result):
        # Function for clients1's specific callback when pubslishing message
        print("Data 10hz Published")
        pass
      
    client, connection = connect_to_broker(client_id=client_id, host=host, port=port, keepalive=keepalive, on_connect=on_connect, on_publish=on_publish)
    
    client.loop_start()

    while True:
        values = np.empty((0, 4)) #create an empty array with 4 'columns'
        for _ in range(600): # The following should be repeated 600 times to complete a minute
            now = time.time() #Time measurement to know how long this procedure takes
            values = np.vstack((values, np.array([1, 1, datetime.now(), adc0.read_adc(0, gain=GAIN, data_rate=data_rate)])))
            values = np.vstack((values, np.array([1, 2, datetime.now(), adc0.read_adc(1, gain=GAIN, data_rate=data_rate)])))
            values = np.vstack((values, np.array([1, 3, datetime.now(), adc0.read_adc(2, gain=GAIN, data_rate=data_rate)])))
            values = np.vstack((values, np.array([1, 4, datetime.now(), adc0.read_adc(3, gain=GAIN, data_rate=data_rate)])))
            values = np.vstack((values, np.array([2, 1, datetime.now(), adc1.read_adc(0, gain=GAIN, data_rate=data_rate)])))
            values = np.vstack((values, np.array([2, 2, datetime.now(), adc1.read_adc(1, gain=GAIN, data_rate=data_rate)])))
            values = np.vstack((values, np.array([2, 3, datetime.now(), adc1.read_adc(2, gain=GAIN, data_rate=data_rate)])))
            values = np.vstack((values, np.array([2, 4, datetime.now(), adc1.read_adc(3, gain=GAIN, data_rate=data_rate)])))
            operation_time = time.time()-now
            if operation_time < 0.1:
                time.sleep(0.1 - operation_time)
        dataframe = pd.DataFrame(values, columns=headers)
        dataframe.to_csv('ten_hz.csv', columns=headers, index=False)
        f = open('ten_hz.csv')
        csv = f.read()
        client.publish(topic, csv, 2)

def read_one_hundred_hz():
    """ 
    Reads channels from last two ADCs at a 1Hz rate, except for the last channel (A3)
    of the last ADC (adc3) which is read at 100Hz
    """
    client_id = "ONE_HUNDRED_HZ" #Different id from the first function
    host = "35.237.36.219" # static IP of mosquitto broker
    port = 1883
    keepalive = 30
    topic = "usa/quincy/1"
    GAIN = 1 # We are going to use same gain for all of them
    headers = ['adc', 'channel', 'time_stamp', 'value'] # Headers of the upcoming csv file
    data_rate = 860

    def on_connect(client, userdata, flags, rc):
        pass

    def on_publish(client, userdata, result):
        # Function for clients1's specific callback when pubslishing message
        print("Data one/hundred Published")
        pass
      
    client, connection = connect_to_broker(client_id=client_id, host=host, port=port, keepalive=keepalive, on_connect=on_connect, on_publish=on_publish)
    
    client.loop_start()

    while True:
        #create an empty array with 4 'columns'
        values = np.empty((0, 4))
        for _ in range(60): # makes 60 loops, assuming the whole operation above takes ~1 second
            # Make one reading of all 1Hz channels on ADCs 2 and 3
            values = np.vstack((values, np.array([3, 1, datetime.now(), adc2.read_adc(0, gain=GAIN, data_rate=data_rate)])))
            values = np.vstack((values, np.array([3, 2, datetime.now(), adc2.read_adc(1, gain=GAIN, data_rate=data_rate)])))
            values = np.vstack((values, np.array([3, 3, datetime.now(), adc2.read_adc(2, gain=GAIN, data_rate=data_rate)])))
            values = np.vstack((values, np.array([3, 4, datetime.now(), adc2.read_adc(3, gain=GAIN, data_rate=data_rate)])))
            values = np.vstack((values, np.array([4, 1, datetime.now(), adc3.read_adc(0, gain=GAIN, data_rate=data_rate)])))
            values = np.vstack((values, np.array([4, 2, datetime.now(), adc3.read_adc(1, gain=GAIN, data_rate=data_rate)])))
            values = np.vstack((values, np.array([4, 3, datetime.now(), adc3.read_adc(2, gain=GAIN, data_rate=data_rate)])))
            # Reads from 4th pin on adc3 @ 100Hz... 
            for _ in range(100): # The following should be repeated 100 times to complete a second
                now = time.time() #Time measurement to know how long this procedure takes
                values = np.vstack((values, np.array([4, 4, datetime.now(), adc3.read_adc(3, gain=GAIN, data_rate=860)])))
                operation_time = time.time()-now
                if operation_time < 0.01:
                    time.sleep(0.01 - operation_time)
        dataframe = pd.DataFrame(values, columns=headers)
        dataframe.to_csv('hundred_hz.csv', columns=headers, index=False)
        f = open('hundred_hz.csv')
        csv = f.read()
        client.publish(topic, csv, 2)

if __name__ == '__main__':
    p_ten_hz = Process(target=read_ten_hz)
    p_hundred_hz = Process(target=read_one_hundred_hz)
    p_ten_hz.start()
    p_hundred_hz.start()
