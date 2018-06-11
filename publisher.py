import paho.mqtt.client as mqtt
import time

mqttc = mqtt.Client("python_pub")
mqttc.connect("35.237.36.219", 1883)
while True:
	mqttc.publish("hello/world", "Hello, World!")
	mqttc.publish("hello/world", "It is fucking working")
mqttc.loop_forever()