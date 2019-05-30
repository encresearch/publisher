
def test_connect_to_broker():
	from publisher.publisher import HOST, PORT, KEEPALIVE, TOPIC, client_id, connect_to_broker
	def on_connect(client, userdata, flags, rc):
		assert rc == 0 # assert the connection is successful
		client.disconnect() # Then disconnect
	def on_publish(client, userdata, result):
		pass # just pass for now
	client, connection = connect_to_broker(client_id=client_id, host=HOST, port=PORT, keepalive=KEEPALIVE, on_connect=on_connect, on_publish=on_publish)
	# Now, lets test a fake connection
	# TODO ^^

def test_reading_from_all_pins():
	from publisher.publisher import Adafruit_ADS1x15, GAIN, data_rate, adc0, adc1, adc2, adc3
	adcs = [adc0, adc1, adc2, adc3]
	for adc in adcs:
		for pin in range(4):
			reading = adc.read_adc(0, gain=GAIN, data_rate=data_rate)
			assert reading > 0

def test_readings_and_rate():
	import pandas as pd
	from publisher.publisher import get_readings
	df = get_readings()
	assert len(df) == 9600
	all_adcs_readings = df['adc'].value_counts()
	for readings in all_adcs_readings:
		assert readings == 2400
	# TODO test rates based on df
	# TODO test headers and formatting are right

def test_send_readings():
	import pandas as pd
	from publisher.publisher import send_readings
	# TODO: Test a CSV is created
	# TODO: Test a CSV file is sent to the broker (with a fake broker container)
	pass
