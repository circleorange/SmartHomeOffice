# Libraries
from sense_hat import SenseHat
import subprocess
import time
from dotenv import dotenv_values
import BlynkLib
import requests

# Used for debugging
debug_mode = False

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


def read_environmental_data():
    # ----- Sense Hat -----
    # Read CPU temperature using the vcgencmd utility and decode bytes object returned by output to regular Unicode string
    cpu_temp_bytes = subprocess.check_output("vcgencmd measure_temp", shell=True).decode() 
    cpu_temp = cpu_temp_bytes.split("=")[1].split("'")[0]

    # Convert the CPU temperature from a string to a float
    cpu_temp = float(cpu_temp)
    if debug_mode == True:
        print("CPU T:", cpu_temp)

    # Read sensor temperature
    temp = sense.get_temperature()
    if debug_mode == True:
        print("Sensor T:", temp)

    # Calibrate temperature
    factor = 1.4
    temp_calibrated = temp - ((cpu_temp - temp)/factor)
    temp_calibrated = float("{0:.2f}".format(temp_calibrated))
    if debug_mode == True:
        print("Calibrated T:", temp_calibrated)

    return temp_calibrated


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


while True:
    blynk.run()
    # read environmental data to from RPi
    current_temp = read_environmental_data()
    # write environmental data to Blynk
    blynk.virtual_write(1, current_temp)
    
    # ----- Limit number of notifications sent to the user ------
    if current_temp > target_temperature and notification_cooldown == 0 and send_notifications and target_temperature is not None:
        send_temperature_notification()
        # While loop sleep time is 0.5 and cooldown 60,
        # then notification can trigger every 30 seconds
        notification_cooldown = 60 
    elif notification_cooldown > 0:
        notification_cooldown -= 1
    
    # ----- Disable heating if temperature has been exceed by 20% -----
    if current_temp > target_temperature + (current_temp * 0.2) and target_temperature is not None and safety_control:
        value = blynk.virtual_write(0, 0)
        power_off_heater()

    time.sleep(.5)