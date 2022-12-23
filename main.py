#!/usr/bin/python3
# Execution command: python main.py mqtt://mqtt3.thingspeak.com:1883

# Libraries
import time
from dotenv import dotenv_values

# Raspberry Pi related libraries
from sense_hat import SenseHat
import subprocess

# Blynk related libraries
import BlynkLib

## IFTTT related libraries
import requests

## ThingSpeak related libraries
import paho.mqtt.client as mqtt
from urllib.parse import urlparse
import sys
import logging

# Load environmental data
config = dotenv_values(".env")

# Initialize Blynk
blynk = BlynkLib.Blynk(config["BLYNK_AUTH_TOKEN"])

# Initialise SenseHAT
sense = SenseHat()
sense.clear()

# Initialize global variables
notification_cooldown = 0
target_temperature = 0
loop_delay = 0.5
mqtt_publish_delay = 30
mqtt_counter = 0

# Initalize logging
logging.basicConfig(level=logging.INFO)

# Initial Switch Configuration
safety_control = True
blynk.virtual_write(0, 0)
send_notifications = False
blynk.virtual_write(3, 0)


# Register handler for virtual pin V0 write event (Power)
@blynk.on("V0")
def v0_power_handler(value):
    button_value = value[0]

    # Read button value to control the device power
    if button_value == "1":
        power_on_heater()
    else:
        power_off_heater()


# Register handler for virtual pin V2 write event (Target Temperature)
@blynk.on("V2")
def v2_slider_callback(value):
    global target_temperature
    target_temperature = int(value[0])


# Register handler for virtual pin V3 write event (Notifications)
@blynk.on("V3")
def v3_notifications_handler(value):
    button_value = value[0]
    global send_notifications
    if button_value == "1":
        send_notifications = True
    else:
        send_notifications = False


# Register handler for virtual pin V4 write event (Safety Control)
@blynk.on("V4")
def v4_safety_control(value):
    button_value = value[0]
    global safety_control
    if button_value == "1":
        safety_control = True
    else:
        safety_control = False

# ----- Raspberry Pi setup -----
def read_environmental_data():
    # ----- Sense Hat -----
    pressure=round(sense.pressure,2)
    humidity=round(sense.humidity,2)

    # Read CPU temperature using the vcgencmd utility and decode bytes object returned by output to regular Unicode string
    cpu_temp_bytes = subprocess.check_output("vcgencmd measure_temp", shell=True).decode() 
    cpu_temp = cpu_temp_bytes.split("=")[1].split("'")[0]

    # Convert the CPU temperature from a string to a float
    cpu_temp = float(cpu_temp)

    # Read sensor temperature
    temp = sense.get_temperature()

    # Calibrate temperature
    factor = 1.4
    temp_calibrated = temp - ((cpu_temp - temp)/factor)
    temp_calibrated = float("{0:.2f}".format(temp_calibrated))

    sensor_data = {
        "Temperature": temp_calibrated, 
        "Pressure": pressure, 
        "Humidity": humidity
        }
    print(sensor_data)
    return sensor_data


def power_on_heater():
    url = 'https://maker.ifttt.com/trigger/turn_on/with/key/'+config["IFTTT_KEY"]
    response = requests.post(url)


def power_off_heater():
    url = 'https://maker.ifttt.com/trigger/turn_off/with/key/'+config["IFTTT_KEY"]
    response = requests.post(url)


# Send temperature exceeded notification
def send_temperature_notification():
    url = 'https://maker.ifttt.com/trigger/temperature_exceeded/with/key/'+config["IFTTT_KEY"]
    response = requests.post(url)

# ----- Thing Speak setup -----
# Define event callbacks for MQTT
def on_connect(client, userdata, flags, rc):
    logging.info("Connection Result: " + str(rc))

def on_publish(client, obj, mid):
    logging.info("Message Sent ID: " + str(mid))

mqttc = mqtt.Client(client_id=config["THINGSPEAK_CLIENT_ID"])

# Assign event callbacks
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish

# parse mqtt url for connection details
url_str = sys.argv[1]
print(url_str)
url = urlparse(url_str)
base_topic = url.path[1:]

# Configure MQTT client with user name and password
mqttc.username_pw_set(config["THINGSPEAK_USERNAME"], config["THINKGSPEAK_PASSWORD"])

#Connect to MQTT Broker
mqttc.connect(url.hostname, url.port)
mqttc.loop_start()

#Set Thingspeak Channel to publish to
topic = "channels/"+config["THINKGSPEAK_CHANNEL_ID"]+"/publish"

# ----- Main loop ----
while True:
    blynk.run()
    # read environmental data to from RPi
    sensor_data = read_environmental_data()
    current_temp = sensor_data["Temperature"]
    # write environmental data to Blynk
    blynk.virtual_write(1, current_temp)
    
    # Limit number of notifications sent to the user
    if current_temp > target_temperature and notification_cooldown == 0 and send_notifications and target_temperature is not None:
        send_temperature_notification()
        # loop_delay is 0.5 and cooldown 60,
        # then notification can trigger every 30 seconds
        notification_cooldown = 60 
    elif notification_cooldown > 0:
        notification_cooldown -= 1
    
    # Disable heating if temperature has been exceed by 20%
    if current_temp > target_temperature + (current_temp * 0.2) and target_temperature is not None and safety_control:
        value = blynk.virtual_write(0, 0)
        power_off_heater()

    # Publish a message to temp every 15 seconds
    mqtt_counter += 1
    if mqtt_counter % (mqtt_publish_delay / loop_delay):
        try:
            payload = f"field1={current_temp}&field2={sensor_data['Humidity']}&field3={sensor_data['Pressure']}"
            mqttc.publish(topic, payload)
        except:
            logging.info('Interrupted')

    time.sleep(loop_delay)
