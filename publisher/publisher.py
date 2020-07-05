"""
This script reads from different Analog to Digital Converters (ADC)
inputs at three established frequencies. It runs two processes at the same
time. They collect data from the first two, and last two ADCs respectively,
writes it to a CSV file, and then sends it to a Mosquitto broker on the cloud.

The devices' GAIN was chosen to be 1. Since this is a 16 bits device,
the measured voltage will depend on the programmable GAIN. The following table
shows the possible reading range per chosen GAIN. A GAIN of 1 goes from
-4.096V to 4.096V.
- 2/3 = +/-6.144V
-   1 = +/-4.096V
-   2 = +/-2.048V
-   4 = +/-1.024V
-   8 = +/-0.512V
-  16 = +/-0.256V

This means that the maximum range of this 16 bits device is +/-32767.
Thus, to convert bits to V, we divide 4.096 by 32767,
which gives us 0.000125. In conclusion, to convert this readings to mV
we just need to multiply the output times by 0.125, which is done in the
server side (connector) to prevent time delays.

All readings are done at 10Hz.

TODO [Magnetometer functions coming up]
"""
import os
import time
from datetime import datetime

if 'x86' in os.uname().machine:
    import warnings
    from publisher.lib import Adafruit_ADS1x15_MOCK_x86 as Adafruit_ADS1x15
    warnings.warn(
        "x86 Machine Detected..."
        " Running publisher in simulation mode"
    )
    TOPIC = os.getenv("PUBLISHER_TOPIC", "test_env/usa/quincy/1")
else:
    import Adafruit_ADS1x15
    TOPIC = os.getenv("PUBLISHER_TOPIC", "usa/quincy/1")

import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np

# For development purposes we are using Eclipse's public mosquitto broker
# static IP.
HOST = os.getenv("BROKER_IP", "mqtt.eclipse.org")
PORT = os.getenv("BROKER_PORT", 1883)
KEEPALIVE = 30
client_id = "{0}".format("/TEN_HZ")

GAIN = 1
data_rate = 475
ADC_INSTANCES_NUM = 2
GENERATED_CSV_FILE_NAME = 'ten_hz.csv'
DF_HEADERS = ['adc', 'channel', 'time_stamp', 'value']

ADC_SAMPLING_RATE = 10 # Hz
SAMPLES_PER_MINUTE = ADC_SAMPLING_RATE * 60
SAMPLING_PERIOD = 1 / ADC_SAMPLING_RATE # secs/sample


def get_adc_ADS1115_objects():
    """This function returns the ADC instances to be used.

    It is able to create two or four (at the moment we are using only two)
    ADS115 instances with different addresses based on the connection of the
    ADR (address) pin:
    - 0x48 (1001000) ADR -> GND
    - 0x49 (1001001) ADR -> VDD
    - 0x4A (1001010) ADR -> SDA
    - 0x4B (1001011) ADR -> SCL

    Data Rate samples are chosen based on the frequency we want to pull data
    from it. data_rate indicates the time it will take in measuring the analog
    data.

    Depending on the platform that's used, the imports will vary (for running
    in simulation mode).

    It will run mock publisher if in an x86 dev machine.
    - TOPIC: <country>/<city>/<device_num>/<reading_type>
    """
    adc0 = Adafruit_ADS1x15.ADS1115(address=0x48)
    adc1 = Adafruit_ADS1x15.ADS1115(address=0x49)

    if ADC_INSTANCES_NUM == 4:
        adc2 = Adafruit_ADS1x15.ADS1115(0x4A)
        adc3 = Adafruit_ADS1x15.ADS1115(0x4B)
        return (adc0, adc1, adc2, adc3)

    return (adc0, adc1)


def on_connect(client, userdata, flags, rc):
    """To be displayed when connected"""
    print("connected with result code {}".format(rc))


def on_publish(client, userdata, result):
    """Function for clients's specific callback when pubslishing message"""
    print("Data 10hz Published")


def connect_to_broker(client_id, host, port, keepalive,):
    """
    Default params of mqtt.Client: ( client_id="", clean_session=True,
    userdata=None, protocol=MQTTv311, transport="tcp" )
    """
    # We set clean_session False, so in case connection is lost,
    # it'll reconnect with same ID
    client = mqtt.Client(client_id=client_id, clean_session=False)
    client.on_connect = on_connect
    client.on_publish = on_publish
    connection = client.connect(host, port, keepalive)
    return (client, connection)


def get_readings(adcs):
    """
    Returns an array of 4 columns with headers -> HEADERS and the ADCs 10Hz
    measurements for each pin, for 1 minute (2,400 readings per ADC).

    | adc | channel | time_stamp |  value  |
    |-----|---------|------------|---------|
    |  0  |    0    |   xxxxxx   |   YYYY  |
    |-----|---------|------------|---------|
    | ... |   ...   |    ...     |   ...   |
    |-----|---------|------------|---------|
    """
    values = np.empty((0, 4)) #create an empty array with 4 'columns'
    for _ in range(SAMPLES_PER_MINUTE):
        # Time measurement to know how long this procedure takes
        now = time.time()
        for adc in enumerate(adcs):
            for pin in range(4):
                values = np.vstack((values, np.array([
                    adc[0],
                    pin,
                    datetime.now(),
                    adc[1].read_adc(pin, gain=GAIN, data_rate=data_rate)
                ])))
        operation_time = time.time()-now
    
        if operation_time < SAMPLING_PERIOD:
            time.sleep(SAMPLING_PERIOD - operation_time)

    dataframe = pd.DataFrame(values, columns=DF_HEADERS)
    return dataframe


def send_readings(dataframe, client):
    """Takes a Pandas' dataframe, creates CSV file and sends through mqtt."""
    dataframe.to_csv(GENERATED_CSV_FILE_NAME, columns=DF_HEADERS, index=False)
    readings_file = open(GENERATED_CSV_FILE_NAME)
    csv = readings_file.read()
    client.publish(TOPIC, csv, 2)


def main():
    """
    Reads from all channels from all adc's ten times in a second,
    creates a numpy array which is then converted to a panda's dataframe and
    into a CSV file and sent to the MQTT broker.

    A dataframe is created every minute and then it is sent to the broker.
    """

    adcs = get_adc_ADS1115_objects()
    client, connection = connect_to_broker(
        client_id=client_id,
        host=HOST,
        port=PORT,
        keepalive=KEEPALIVE
    )

    client.loop_start()

    while True:
        dataframe = get_readings(adcs=adcs)
        send_readings(dataframe, client)
