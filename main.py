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
notifications_enabled = True
notification_cooldown = 0
target_temperature = 0 


# Register handler for virtual pin V0 write event (Power)
@blynk.on("V0")
def v0_power_handler(value):
    button_value = value[0]

    # Read button value to control the device power
    if button_value == "1":
        url = 'https://maker.ifttt.com/trigger/turn_on/with/key/'+config["IFTTT_KEY"]
        response = requests.post(url)
    else:
        url = 'https://maker.ifttt.com/trigger/turn_off/with/key/'+config["IFTTT_KEY"]
        response = requests.post(url)


# Register handler for virtual pin V2 write event (Target Temperature)
@blynk.on("V2")
def v2_slider_callback(value):
    global target_temperature
    target_temperature = int(value[0])


# Register handler for virtual pin V3 write event (Notifications)
@blynk.on("V3")
def v3_notifications_handler(value):
    button_value = value[0]
    global notifications_enabled
    if button_value == "1":
        notifications_enabled = True
    else:
        notifications_enabled = False


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
    factor = 1.6
    temp_calibrated = temp - ((cpu_temp - temp)/factor)
    temp_calibrated = float("{0:.2f}".format(temp_calibrated))
    if debug_mode == True:
        print("Calibrated T:", temp_calibrated)

    return temp_calibrated


# Send temperature exceeded notification
def send_temperature_notification():
    url = 'https://maker.ifttt.com/trigger/temperature_exceeded/with/key/'+config["IFTTT_KEY"]
    response = requests.post(url)



while True:
    blynk.run()
    temperature = read_environmental_data()
    blynk.virtual_write(1, temperature) # write environmental data to Blynk

    # ----- Limit number of notifications sent to the user -----
    if temperature >= target_temperature and notification_cooldown == 0 and notifications_enabled:
        send_temperature_notification()
        # Loop sleep time is 0.5 and cooldown 60, then notification can trigger every 30 seconds
        notification_cooldown = 10 
    elif notification_cooldown > 0:
        notification_cooldown -= 1
    
    time.sleep(.5)