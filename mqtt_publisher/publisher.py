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

# create four ADS115 instances 
adc0 = Adafruit_ADS1x15.ADS1115(0x48) # ADR to GRN
adc1 = Adafruit_ADS1x15.ADS1115(0x49) # ADR to VDD
adc2 = Adafruit_ADS1x15.ADS1115(0x4A) # ADR to SDA
adc3 = Adafruit_ADS1x15.ADS1115(0x4B) # ADR to SCL

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
    GAIN = 1 # We are going to use same gain for all of them
    headers = ['adc', 'channel', 'time_stamp', 'value'] # Headers of the upcoming csv file

    def on_connect(client, userdata, flags, rc):
        pass

    def on_publish(client, userdata, result):
        # Function for clients1's specific callback when pubslishing message
        print("Data Published")
        pass
      
    client, connection = connect_to_broker(client_id=client_id, host=host, port=port, keepalive=keepalive, on_connect=on_connect, on_publish=on_message)
    
    client.loop_start()

    while True:
        values = np.empty((0, 4)) #create an empty array with 4 'columns'
        for _ in range(600): # The following should be repeated 600 times to complete a minute
            now = time.time() #Time measurement to know how long this procedure takes
            values = np.vstack((values, np.array([1, 1, datetime.now(), adc0.read_adc(0, gain=GAIN)])))
            values = np.vstack((values, np.array([1, 2, datetime.now(), adc0.read_adc(1, gain=GAIN)])))
            values = np.vstack((values, np.array([1, 3, datetime.now(), adc0.read_adc(2, gain=GAIN)])))
            values = np.vstack((values, np.array([1, 4, datetime.now(), adc0.read_adc(3, gain=GAIN)])))
            values = np.vstack((values, np.array([2, 1, datetime.now(), adc1.read_adc(0, gain=GAIN)])))
            values = np.vstack((values, np.array([2, 2, datetime.now(), adc1.read_adc(1, gain=GAIN)])))
            values = np.vstack((values, np.array([2, 3, datetime.now(), adc1.read_adc(2, gain=GAIN)])))
            values = np.vstack((values, np.array([2, 4, datetime.now(), adc1.read_adc(3, gain=GAIN)])))
            operation_time = time.time()-now
            if operation_time < 0.1:
                time.sleep(0.1 - operation_time)
        dataframe = pd.DataFrame(values, columns=headers)
        dataframe.to_csv('ten_hz.csv', columns=headers, index=False)
        f = open('ten_hz.csv')
        csv = f.read()
        client.publish("RasPi1/10Hz", csv, 2)

def main():
    read_ten_hz()

if __name__ == '__main__':
    main()