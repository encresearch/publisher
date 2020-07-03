"""File with most reading tests"""
import os

import pytest
import pandas as pd

from publisher.publisher import (
    HOST,
    PORT,
    KEEPALIVE,
    TOPIC,
    ADC_INSTANCES_NUM,
    SAMPLES_PER_MINUTE,
    GENERATED_CSV_FILE_NAME,
    GAIN,
    data_rate,
    connect_to_broker,
    get_adc_ADS1115_objects,
    get_readings,
    send_readings
)

TEST_CLIENT_ID = 'test_client'


def test_connect_to_broker():
    """Test that our broker connection is working fine.
    This doens't need to run in a RasPi.
    """
    client, connection = connect_to_broker(
        client_id='test_client',
        host=HOST,
        port=PORT,
        keepalive=KEEPALIVE
    )
    assert client is not None
    assert connection is not None
    client.disconnect()


def test_get_adc_ADS1115_objects():
    """Test ADC's are instantiated correctly."""
    adcs = get_adc_ADS1115_objects()
    sample_reading = adcs[0].read_adc(0, gain=GAIN, data_rate=data_rate)
    assert len(adcs) == ADC_INSTANCES_NUM
    assert sample_reading is not None


def test_get_readings():
    """Test the function that gets our readings in the determined frequency."""
    # No. of rows = samples_per_minute * num_of_adcs * 4_pins_per_ADC
    expected_df_samples_num = SAMPLES_PER_MINUTE * ADC_INSTANCES_NUM * 4
    expected_individual_adc_sample_count = SAMPLES_PER_MINUTE * 4

    adc0, adc1 = get_adc_ADS1115_objects()
    df = get_readings(adc0, adc1)
    all_adcs_readings = df['adc'].value_counts()

    assert len(df) == expected_df_samples_num
    for readings in all_adcs_readings:
        assert readings == expected_individual_adc_sample_count


def test_expected_readings():
    """Outputs real readings from all pins for calibration purposes."""
    adc0, adc1 = get_adc_ADS1115_objects()
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
            reading = adc[1].read_adc(
                pin,
                gain=GAIN,
                data_rate=data_rate
            )*0.125
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


def test_send_readings():
    """Test our func that sends ADC readings."""
    # TODO: Test a CSV file is sent to the broker (with a fake broker container)
    adc0, adc1 = get_adc_ADS1115_objects()
    dataframe = get_readings(adc0=adc0, adc1=adc1)
    dir_path = os.path.dirname(os.path.realpath(__file__))

    client, connection = connect_to_broker(
        client_id=TEST_CLIENT_ID,
        host=HOST,
        port=PORT,
        keepalive=KEEPALIVE
    )

    client.loop_start()
    send_readings(dataframe, client)

    # test a csv file is created
    assert os.path.exists('{path}/../{file}'.format(
        path=dir_path,
        file=GENERATED_CSV_FILE_NAME
    ))

    client.loop_stop()
    client.disconnect()
