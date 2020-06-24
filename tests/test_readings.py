"""File with most reading tests"""
import pytest

def test_connect_to_broker():
    from publisher.publisher import (
        HOST, PORT, KEEPALIVE, TOPIC, client_id, connect_to_broker
    )
    def on_connect(client, userdata, flags, rc):
        assert rc == 0 # assert the connection is successful
        client.disconnect() # Then disconnect
    def on_publish(client, userdata, result):
        pass # just pass for now
    client, connection = connect_to_broker(
        client_id=client_id,
        host=HOST,
        port=PORT,
        keepalive=KEEPALIVE,
        on_connect=on_connect,
        on_publish=on_publish
    )
    import pdb; pdb.set_trace()
    # Now, lets test a fake connection

@pytest.fixture
def readings_df():
    from publisher.publisher import get_readings
    df = get_readings()
    return df

def test_expected_readings():
    """Outputs readings from all pins for calibration purposes."""
    from publisher.publisher import (
        Adafruit_ADS1x15,
        GAIN,
	data_rate,
        adc0,
        adc1
    )
    adcs = [(0, adc0), (1, adc1)]
    readings = []
    ansi_code_yellow_init = "\033[93m"
    ansi_code_yellow_end = "\033[00m"
    for adc in adcs:
        print('\n{}ADC: {}{}'.format(
            ansi_code_yellow_init,
            adc[0],
            ansi_code_yellow_end
        )),
        for pin in range(4):
            reading = adc[1].read_adc(pin, gain=GAIN, data_rate=data_rate)*0.125
            assert reading is not None
            readings.append(reading)
            print('\t{}PIN: {}, READING: {} mV{}'.format(
                ansi_code_yellow_init,
                pin,
                reading,
                ansi_code_yellow_end
            ))
    if not all(reading is None for reading in readings):
        print("\n{}{}\n{}{}".format(
            ansi_code_yellow_init,
            "PLEASE MAKE SURE ALL READ VALUES ARE EXPECTED",
            ('#'*50),
            ansi_code_yellow_end
        ))

def test_readings_and_rate(readings_df):
    """Reads measurements for one minute."""
    import pandas as pd
    df = readings_df
    assert len(df) == 4800 # TODO Change this to an actual sensor count function
    all_adcs_readings = df['adc'].value_counts()
    for readings in all_adcs_readings:
        assert readings == 2400
    # TODO test rates based on df

""" TODO
def test_send_readings(readings_df):
    import os
    import pandas as pd
    from publisher.publisher import send_readings, connect_to_broker

    HOST = os.getenv("BROKER_IP", "mqtt.eclipse.org")
    PORT = os.getenv("BROKER_PORT", 1883)
    KEEPALIVE = 30
    TOPIC = os.getenv("TOPIC", "usa/quincy/testing-pi")
    GAIN = 1
    DF_HEADERS = ['adc', 'channel', 'time_stamp', 'value']
    client_id = "{0}".format("/TEN_HZ")
    data_rate = 475

    client, connection = connect_to_broker(
        client_id=client_id,
        host=HOST,
        port=PORT,
        keepalive=KEEPALIVE,
        on_connect=None,
        on_publish=None
    )

    dir_path = os.path.dirname(os.path.realpath(__file__))
    send_readings(readings_df, client)
    # test a csv file is created
    assert os.path.exists('{path}/{file}'.format(
        path=dir_path,
        file='ten_hz.csv'
    ))
    # TODO: Test a CSV file is sent to the broker (with a fake broker container)
    pass
"""

